import os, hashlib, tempfile
from minio import Minio
from langchain_unstructured import UnstructuredLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain.schema import Document

# 参数配置
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BUCKET_NAME = "suifang"
CHROMA_DIR = os.path.join(CURRENT_DIR, "chroma_db")
EMBEDDING_MODEL = "nomic-embed-text"
HASH_RECORD_FILE = os.path.join(CURRENT_DIR,"processed_hashes.txt")

minio_client = Minio("170.106.150.85:31000", access_key="minioadmin", secret_key="minioadmin123", secure=False)
embedding = OllamaEmbeddings(model=EMBEDDING_MODEL)

def calculate_file_hash(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def sync_documents():
    if not os.path.exists(HASH_RECORD_FILE):
        open(HASH_RECORD_FILE, 'w').close()

    with open(HASH_RECORD_FILE, 'r') as f:
        processed_hashes = set(line.strip() for line in f)

    if os.path.exists(CHROMA_DIR):
        db = Chroma(persist_directory=CHROMA_DIR, embedding_function=embedding)
    else:
        empty_doc = Document(page_content="", metadata={})
        db = Chroma.from_documents([empty_doc], embedding, persist_directory=CHROMA_DIR)

    updated = 0
    for obj in minio_client.list_objects(BUCKET_NAME, recursive=True):
        # 创建临时文件并关闭
        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        tmp_file_path = tmp_file.name
        tmp_file.close()

        # 下载文件到临时路径
        minio_client.fget_object(BUCKET_NAME, obj.object_name, tmp_file_path)

        file_hash = calculate_file_hash(tmp_file_path)
        if file_hash in processed_hashes:
            os.remove(tmp_file_path)
            continue

        try:
            loader = UnstructuredLoader(tmp_file_path)
            docs = loader.load()
        except Exception as e:
            print(f"❌ 无法解析 {obj.object_name}: {e}")
            os.remove(tmp_file_path)
            continue

        # 文本分割
        chunks = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100
        ).split_documents(docs)

        # 添加文档到向量数据库
        chunks = filter_complex_metadata(chunks)
        db.add_documents(chunks)

        # 更新哈希记录
        with open(HASH_RECORD_FILE, 'a') as f:
            f.write(file_hash + '\n')

        updated += 1

        # 删除临时文件
        os.remove(tmp_file_path)

    return f"✅ 同步完成，新增文档数量: {updated}"

if __name__ == '__main__':
    print(sync_documents())