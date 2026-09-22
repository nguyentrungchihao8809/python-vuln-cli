from huggingface_hub import HfApi, create_repo

REPO_ID = "haoday333/python-vuln-codebert"  # SUA LAI dung username va ten repo ban da tao
import os
LOCAL_MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models", "codebert_finetuned")

api = HfApi()

# Tao repo neu chua ton tai (khong loi neu da ton tai san)
create_repo(repo_id=REPO_ID, exist_ok=True)

api.upload_folder(
    folder_path=LOCAL_MODEL_DIR,
    repo_id=REPO_ID,
    repo_type="model"
)

print(f"Da upload xong model len: https://huggingface.co/{REPO_ID}")