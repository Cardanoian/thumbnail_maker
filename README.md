# 썸네일 PDF 변환기

PDF 또는 이미지를 **20KB 이하** 단일 페이지 PDF로 바꿉니다. 결과는 20,480바이트를 넘지 않습니다.

## 사용자용

1. `dist\ThumbnailMaker_Setup.exe`를 실행해 설치합니다.
2. 바탕화면의 **썸네일 PDF 변환기**를 엽니다.
3. 파일을 끌어다 놓거나 **파일 선택** 후 **변환하기**를 누릅니다.

설치 파일이 없다면 `dist\ThumbnailMaker\ThumbnailMaker.exe`를 실행해도 됩니다.

## 개발용

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m pytest
.\.venv\Scripts\python run.py
```

Windows exe / 설치 파일:

```powershell
powershell -ExecutionPolicy Bypass -File build\build.ps1
```

Inno Setup 6이 있으면 `ThumbnailMaker_Setup.exe`까지 만들고, 없으면 `ThumbnailMaker.exe` 폴더만 만듭니다.
