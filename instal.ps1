

# Création du répertoire d'installation
New-Item -ItemType Directory -Path C:\tmp\iauskour_install -Force | Out-Null

& pip install virtualenv
& virtualenv venv --python=python3.11

Write-Host "Environnement virtuel créé avec succès."

# Activation de l'environnement virtuel
.\venv\Scripts\Activate.ps1

# Installation des dépendances du projet depuis le fichier requirements.txt
$requirementsFile = "./requirements.txt"
if (Test-Path $requirementsFile) {
    & pip install -r $requirementsFile
       Write-Host "Le fichier requirements.txt a été trouvé."
} else {
    Write-Host "Le fichier requirements.txt n'a pas été trouvé."
}

& winget install kitware.cmake

# Récupérer le chemin d'installation de CMake
$cmake= "C:\Program Files\CMake\bin\cmake.exe"

# Vérifier si cmake est reconnu maintenant
& $cmake --version
New-Item -ItemType Directory -Path ./llama/build
Set-Location ./llama/build
& $cmake ..
& $cmake --build --config Release