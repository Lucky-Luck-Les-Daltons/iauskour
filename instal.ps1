

# Création du répertoire d'installation
New-Item -ItemType Directory -Path C:\tmp\iauskour_install -Force | Out-Null

& pip install virtualenv
& virtualenv venv --python=python3.11

Write-Host "Environnement virtuel créé avec succès."

# Activation de l'environnement virtuel
.\venv\Scripts\Activate.ps1

# Installation des dépendances du projet depuis le fichier requirements.txt
$requirementsFile = "./requirements_win.txt"
if (Test-Path $requirementsFile) {
    & python -m pip install -r $requirementsFile
       Write-Host "Le fichier requirements.txt a été trouvé."
} else {
    Write-Host "Le fichier requirements.txt n'a pas été trouvé."
}
