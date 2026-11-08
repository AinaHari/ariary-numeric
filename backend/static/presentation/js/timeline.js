// Timeline configuration for Ariary Numeric Presentation
// Each scene has: id, duration (ms), subtitle text, audio file

const TIMELINE = [
  {
    id: 'scene-01',
    name: 'Introduction',
    duration: 8000,
    subtitle: 'Le monde évolue. Vos échanges aussi. Découvrez Ariary Numeric.',
    audio: 'assets/audio/narration-01.mp3',
    cursor: null
  },
  {
    id: 'scene-02',
    name: 'Page d\'accueil',
    duration: 10000,
    subtitle: 'Une plateforme qui réunit services numériques, gestion des échanges et suivi logistique.',
    audio: 'assets/audio/narration-02.mp3',
    cursor: { start: { x: 100, y: 100 }, end: { x: 400, y: 300 }, clickAt: 5000 }
  },
  {
    id: 'scene-03',
    name: 'Inscription',
    duration: 12000,
    subtitle: 'Créez votre compte en quelques secondes. Aucun document requis.',
    audio: 'assets/audio/narration-03.mp3',
    cursor: { start: { x: 300, y: 200 }, end: { x: 500, y: 400 }, clickAt: 6000, typing: true }
  },
  {
    id: 'scene-04',
    name: 'Portefeuille',
    duration: 12000,
    subtitle: 'Consultez votre solde, votre historique et gérez vos opérations en toute simplicité.',
    audio: 'assets/audio/narration-04.mp3',
    cursor: { start: { x: 200, y: 150 }, end: { x: 600, y: 350 }, clickAt: 4000 }
  },
  {
    id: 'scene-05',
    name: 'Transfert',
    duration: 14000,
    subtitle: 'Envoyez de l\'argent à vos proches en quelques clics. Rapide et sécurisé.',
    audio: 'assets/audio/narration-05.mp3',
    cursor: { start: { x: 400, y: 200 }, end: { x: 700, y: 500 }, clickAt: 5000 }
  },
  {
    id: 'scene-06',
    name: 'QR Code',
    duration: 10000,
    subtitle: 'Générez votre QR code de réception et recevez des paiements instantanément.',
    audio: 'assets/audio/narration-06.mp3',
    cursor: { start: { x: 500, y: 300 }, end: { x: 300, y: 400 }, clickAt: 4000 }
  },
  {
    id: 'scene-07',
    name: 'Transit',
    duration: 14000,
    subtitle: 'Suivez vos marchandises par bateau ou par avion. Chronologie complète et documents associés.',
    audio: 'assets/audio/narration-07.mp3',
    cursor: { start: { x: 200, y: 250 }, end: { x: 800, y: 400 }, clickAt: 6000 }
  },
  {
    id: 'scene-08',
    name: 'Traçabilité',
    duration: 12000,
    subtitle: 'Chaque opération laisse une empreinte numérique vérifiable. Transparence et sécurité.',
    audio: 'assets/audio/narration-08.mp3',
    cursor: { start: { x: 300, y: 200 }, end: { x: 600, y: 300 }, clickAt: 5000 }
  },
  {
    id: 'scene-09',
    name: 'Sécurité',
    duration: 10000,
    subtitle: 'Vos données sont protégées. Transactions atomiques, journal d\'audit, permissions strictes.',
    audio: 'assets/audio/narration-09.mp3',
    cursor: { start: { x: 400, y: 300 }, end: { x: 200, y: 200 }, clickAt: 4000 }
  },
  {
    id: 'scene-10',
    name: 'Conclusion',
    duration: 10000,
    subtitle: 'Simplifiez vos échanges. Explorez de nouvelles possibilités. Ariary Numeric — Madagascar connecté au monde.',
    audio: 'assets/audio/narration-10.mp3',
    cursor: null
  }
];

// Calculate total duration
const TOTAL_DURATION = TIMELINE.reduce((sum, scene) => sum + scene.duration, 0);

// Scene start times
const SCENE_STARTS = [];
let cumulative = 0;
TIMELINE.forEach((scene, index) => {
  SCENE_STARTS.push(cumulative);
  cumulative += scene.duration;
});

function getSceneAtTime(time) {
  for (let i = TIMELINE.length - 1; i >= 0; i--) {
    if (time >= SCENE_STARTS[i]) {
      return { scene: TIMELINE[i], index: i, localTime: time - SCENE_STARTS[i] };
    }
  }
  return { scene: TIMELINE[0], index: 0, localTime: time };
}

function getProgress(time) {
  return Math.min(time / TOTAL_DURATION, 1);
}