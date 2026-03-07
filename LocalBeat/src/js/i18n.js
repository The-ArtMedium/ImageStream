```javascript
// PATH: ImageStream/LocalBeat/src/js/i18n.js

const LANGUAGES={
  en:{dir:"ltr",play:"Play",pause:"Pause",stop:"Stop",
    addLayer:"Add a Layer",import:"Import",samples:"Samples",
    generate:"Generate",mix:"Mix",save:"Save Project",
    export:"Send to LocalEdit",settings:"Settings",
    simpleMode:"Simple Mode",fullMode:"Full Mode",
    volume:"Volume",clip:"Clip",mute:"Mute",remove:"Remove",
    layer:"Layer",confirmRemove:"Remove this layer? This cannot be undone.",
    yes:"Yes",no:"No, keep it",sampleLib:"Sample Library",
    beats:"Beats",ambient:"Ambient",world:"World",tones:"Tones",fx:"FX",
    preview:"Preview",addToLayer:"Add to Layer",
    generateTitle:"Generate Sound",settingsTitle:"Settings",
    language:"Language",textSize:"Text Size",uiScale:"UI Scale",
    highContrast:"High Contrast",aiPlugins:"AI Plugins (optional)",
    about:"About LocalBeat",
    small:"Small",medium:"Medium",large:"Large",extraLarge:"Extra Large"},
  es:{dir:"ltr",play:"Reproducir",pause:"Pausa",stop:"Detener",
    addLayer:"Agregar Capa",import:"Importar",samples:"Muestras",
    generate:"Generar",mix:"Mezclar",save:"Guardar Proyecto",
    export:"Enviar a LocalEdit",settings:"Ajustes",
    simpleMode:"Modo Simple",fullMode:"Modo Completo",
    volume:"Volumen",clip:"Cortar",mute:"Silenciar",remove:"Eliminar",
    layer:"Capa",confirmRemove:"¿Eliminar esta capa? Esta acción no se puede deshacer.",
    yes:"Sí",no:"No, mantener",sampleLib:"Biblioteca de Muestras",
    beats:"Ritmos",ambient:"Ambiente",world:"Mundial",tones:"Tonos",fx:"Efectos",
    preview:"Vista previa",addToLayer:"Añadir a Capa",
    generateTitle:"Generar Sonido",settingsTitle:"Ajustes",
    language:"Idioma",textSize:"Tamaño de Texto",uiScale:"Escala de Interfaz",
    highContrast:"Alto Contraste",aiPlugins:"Plugins de IA (opcional)",
    about:"Acerca de LocalBeat",
    small:"Pequeño",medium:"Mediano",large:"Grande",extraLarge:"Extra Grande"},
  fr:{dir:"ltr",play:"Lecture",pause:"Pause",stop:"Arrêt",
    addLayer:"Ajouter une Piste",import:"Importer",samples:"Échantillons",
    generate:"Générer",mix:"Mixer",save:"Sauvegarder",
    export:"Envoyer à LocalEdit",settings:"Paramètres",
    simpleMode:"Mode Simple",fullMode:"Mode Complet",
    volume:"Volume",clip:"Couper",mute:"Muet",remove:"Supprimer",
    layer:"Piste",confirmRemove:"Supprimer cette piste ? Action irréversible.",
    yes:"Oui",no:"Non, garder",sampleLib:"Bibliothèque d'Échantillons",
    beats:"Rythmes",ambient:"Ambiance",world:"Monde",tones:"Tons",fx:"Effets",
    preview:"Aperçu",addToLayer:"Ajouter à la Piste",
    generateTitle:"Générer un Son",settingsTitle:"Paramètres",
    language:"Langue",textSize:"Taille du Texte",uiScale:"Échelle Interface",
    highContrast:"Contraste Élevé",aiPlugins:"Plugins IA (optionnel)",
    about:"À propos de LocalBeat",
    small:"Petit",medium:"Moyen",large:"Grand",extraLarge:"Très Grand"},
  pt:{dir:"ltr",play:"Reproduzir",pause:"Pausar",stop:"Parar",
    addLayer:"Adicionar Camada",import:"Importar",samples:"Amostras",
    generate:"Gerar",mix:"Mixar",save:"Salvar Projeto",
    export:"Enviar para LocalEdit",settings:"Configurações",
    simpleMode:"Modo Simples",fullMode:"Modo Completo",
    volume:"Volume",clip:"Cortar",mute:"Mudo",remove:"Remover",
    layer:"Camada",confirmRemove:"Remover esta camada? Esta ação não pode ser desfeita.",
    yes:"Sim",no:"Não, manter",sampleLib:"Biblioteca de Amostras",
    beats:"Batidas",ambient:"Ambiente",world:"Mundial",tones:"Tons",fx:"Efeitos",
    preview:"Pré-visualizar",addToLayer:"Adicionar à Camada",
    generateTitle:"Gerar Som",settingsTitle:"Configurações",
    language:"Idioma",textSize:"Tamanho do Texto",uiScale:"Escala da Interface",
    highContrast:"Alto Contraste",aiPlugins:"Plugins de IA (opcional)",
    about:"Sobre o LocalBeat",
    small:"Pequeno",medium:"Médio",large:"Grande",extraLarge:"Extra Grande"},
  ar:{dir:"rtl",play:"تشغيل",pause:"إيقاف مؤقت",stop:"إيقاف",
    addLayer:"إضافة طبقة",import:"استيراد",samples:"عينات",
    generate:"إنشاء",mix:"مزج",save:"حفظ المشروع",
    export:"إرسال إلى LocalEdit",settings:"الإعدادات",
    simpleMode:"الوضع البسيط",fullMode:"الوضع الكامل",
    volume:"الصوت",clip:"قص",mute:"كتم",remove:"حذف",
    layer:"طبقة",confirmRemove:"حذف هذه الطبقة؟ لا يمكن التراجع عن هذا الإجراء.",
    yes:"نعم",no:"لا، احتفظ بها",sampleLib:"مكتبة العينات",
    beats:"إيقاعات",ambient:"أجواء",world:"عالمي",tones:"نغمات",fx:"مؤثرات",
    preview:"معاينة",addToLayer:"إضافة إلى الطبقة",
    generateTitle:"إنشاء صوت",settingsTitle:"الإعدادات",
    language:"اللغة",textSize:"حجم النص",uiScale:"مقياس الواجهة",
    highContrast:"تباين عالٍ",aiPlugins:"إضافات الذكاء الاصطناعي (اختياري)",
    about:"حول LocalBeat",
    small:"صغير",medium:"متوسط",large:"كبير",extraLarge:"كبير جداً"},
  zh:{dir:"ltr",play:"播放",pause:"暂停",stop:"停止",
    addLayer:"添加轨道",import:"导入",samples:"音效库",
    generate:"生成",mix:"混音",save:"保存项目",
    export:"发送到 LocalEdit",settings:"设置",
    simpleMode:"简单模式",fullMode:"完整模式",
    volume:"音量",clip:"裁剪",mute:"静音",remove:"删除",
    layer:"轨道",confirmRemove:"删除此轨道？此操作无法撤销。",
    yes:"是",no:"否，保留",sampleLib:"音效样本库",
    beats:"节拍",ambient:"环境音",world:"世界",tones:"音调",fx:"音效",
    preview:"预览",addToLayer:"添加到轨道",
    generateTitle:"生成声音",settingsTitle:"设置",
    language:"语言",textSize:"字体大小",uiScale:"界面缩放",
    highContrast:"高对比度",aiPlugins:"AI 插件（可选）",
    about:"关于 LocalBeat",
    small:"小",medium:"中",large:"大",extraLarge:"特大"},
  hi:{dir:"ltr",play:"चलाएं",pause:"रोकें",stop:"बंद करें",
    addLayer:"परत जोड़ें",import:"आयात करें",samples:"नमूने",
    generate:"बनाएं",mix:"मिक्स",save:"प्रोजेक्ट सहेजें",
    export:"LocalEdit को भेजें",settings:"सेटिंग्स",
    simpleMode:"सरल मोड",fullMode:"पूर्ण मोड",
    volume:"वॉल्यूम",clip:"काटें",mute:"म्यूट",remove:"हटाएं",
    layer:"परत",confirmRemove:"यह परत हटाएं? यह क्रिया पूर्ववत नहीं की जा सकती।",
    yes:"हाँ",no:"नहीं, रखें",sampleLib:"सैंपल लाइब्रेरी",
    beats:"बीट्स",ambient:"परिवेश",world:"विश्व",tones:"स्वर",fx:"प्रभाव",
    preview:"पूर्वावलोकन",addToLayer:"परत में जोड़ें",
    generateTitle:"ध्वनि बनाएं",settingsTitle:"सेटिंग्स",
    language:"भाषा",textSize:"पाठ का आकार",uiScale:"UI स्केल",
    highContrast:"उच्च कंट्रास्ट",aiPlugins:"AI प्लगइन (वैकल्पिक)",
    about:"LocalBeat के बारे में",
    small:"छोटा",medium:"मध्यम",large:"बड़ा",extraLarge:"बहुत बड़ा"}
};
let currentLang="en";
function setLanguage(code){
  if(!LANGUAGES[code])return;
  currentLang=code;
  document.documentElement.lang=code;
  document.documentElement.dir=LANGUAGES[code].dir;
  localStorage.setItem("localbeat_lang",code);
  applyTranslations(LANGUAGES[code]);
}
function t(key){return LANGUAGES[currentLang][key]||LANGUAGES["en"][key]||key;}
function applyTranslations(lang){
  document.querySelectorAll("[data-i18n]").forEach(el=>{
    const key=el.getAttribute("data-i18n");
    if(lang[key])el.textContent=lang[key];
  });
}
document.addEventListener("DOMContentLoaded",()=>{
  const saved=localStorage.getItem("localbeat_lang")||"en";
  setLanguage(saved);
  const sel=document.getElementById("langSelect");
  if(sel){sel.value=saved;sel.addEventListener("change",e=>setLanguage(e.target.value));}
});
