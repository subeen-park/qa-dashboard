import os

# 제외할 폴더
exclude_dirs = ['.git', '__pycache__', 'venv', 'node_modules', '.streamlit']
# 포함할 확장자
# 수정된 필터 설정 (프론트엔드 파일 포함)
include_exts = ['.py', '.yaml', '.toml', '.txt', '.vue', '.js', '.json']

with open('total_code.txt', 'w', encoding='utf-8') as outfile:
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if any(file.endswith(ext) for ext in include_exts):
                file_path = os.path.join(root, file)
                outfile.write(f"\n\n{'='*20}\nFILE: {file_path}\n{'='*20}\n")
                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        outfile.write(infile.read())
                except:
                    outfile.write("// [파일을 읽을 수 없습니다]\n")