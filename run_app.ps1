# PowerShell launcher for Resume Skill Extractor
$pyPath = "C:\Users\sumiy\AppData\Local\Programs\Python\Python311"
$scriptsPath = "C:\Users\sumiy\AppData\Local\Programs\Python\Python311\Scripts"
$env:Path = "$pyPath;$scriptsPath;$env:Path"

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Launching Resume Skill Extractor (Streamlit Web App)" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan

streamlit run app.py
