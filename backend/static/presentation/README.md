# Ariary Numeric — Présentation Simulée

Présentation vidéo simulée de l'application Ariary Numeric, créée avec HTML, CSS et JavaScript.

## Lancement

### Option 1 : Serveur local (recommandé)
```bash
cd ariary-numeric-presentation
python3 -m http.server 8080
# Ouvrir http://localhost:8080
```

### Option 2 : Ouvrir directement
Ouvrir `index.html` dans un navigateur moderne (Chrome, Firefox, Edge).

## Contrôles
- **Play** : Lancer la présentation
- **Pause** : Mettre en pause
- **Restart** : Recommencer
- **Barre de progression** : Navigation dans la timeline
- **Volume voix** : Régler le volume de la narration
- **Volume musique** : Régler le volume de la musique d'ambiance
- **Muet** : Couper/rétablir le son
- **CC** : Activer/désactiver les sous-titres
- **Plein écran** : Mode plein écran

## Export vidéo MP4

### Prérequis
```bash
# Node.js
sudo apt install nodejs npm
# Playwright
npm install playwright
npx playwright install chromium
# FFmpeg
sudo apt install ffmpeg
```

### Export
```bash
node export-video.js
```

La vidéo sera générée dans `ariary-numeric-presentation.mp4` (1920×1080, 30 FPS).

## Structure
```
ariary-numeric-presentation/
├── index.html          # Point d'entrée
├── scenes/             # 10 scènes HTML
├── css/                # Styles globaux, animations, sous-titres
├── js/                 # Timeline, player, cursor, audio, subtitles
├── assets/             # Images, icônes, audio, logo
├── export-video.js     # Script d'export MP4
└── README.md           # Ce fichier
```

## Scènes
1. **Introduction** — Apparition du logo et slogan
2. **Page d'accueil** — Interface publique avec curseur animé
3. **Inscription** — Formulaire fictif avec saisie simulée
4. **Portefeuille** — Tableau de bord avec solde et historique
5. **Transfert** — Démonstration de transfert fictif
6. **QR Code** — Génération et scan simulé
7. **Transit** — Suivi logistique avec carte et chronologie
8. **Traçabilité** — Animation blockchain et empreintes
9. **Sécurité** — Fonctionnalités de protection
10. **Conclusion** — Logo, slogan et boutons d'action

## Audio
Les fichiers audio de narration doivent être placés dans `assets/audio/` :
- `narration-01.mp3` à `narration-10.mp3`

Sans fichiers audio, la présentation fonctionne avec les sous-titres uniquement.

## Note importante
Cette présentation est une **simulation marketing**. Aucune transaction réelle n'est effectuée. Aucune donnée personnelle n'est collectée. Le portefeuille affiché est un portefeuille de démonstration.