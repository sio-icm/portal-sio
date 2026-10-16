export default {
  comun: {
    nombreServicio: "Servei d'Enginyeria Oceanogràfica",
    contacto: 'CONTACTE',
    intranet: 'INTRANET',
    idiomas: 'Idioma',
    inicio: 'Inici',
    menu: {
      sio: 'EL SIO',
      servicios: 'SERVEIS',
      proyectos: 'PROJECTES',
      idi: 'R+D+I'
    },
    pie: "© 2026 Servei d'Enginyeria Oceanogràfica - CSIC"
  },

  rutas: {
    servicios: 'Serveis',
    instrumentacion: 'Instrumentació',
    pelagia: 'Embarcació Pelagia',
    tanques: 'Tancs de proves',
    salinidad: 'Anàlisi de salinitat',
    fondeos: 'Fondejos',
    prototipado: 'Prototipatge',
    proyectos: 'Projectes',
    idi: 'R+D+I',
    bluelab: 'BLUE Lab',
    equipo: 'Equip',
    noticias: 'Notícies',
    memoria: 'Memòria anual',
    contacto: 'Contacte',
    intranet: 'Intranet',
    noEncontrado: 'Pàgina no trobada'
  },

  inicio: {
    titulo: "Servei d'Enginyeria Oceanogràfica (SIO) · ICM-CSIC",
    carrusel: {
      peces: {
        texto: "Suport tècnic especialitzat en l'àmbit de les ciències del mar",
        alt: "Banc de peixos formant una esfera sota l'aigua"
      },
      niskin: {
        texto: 'Equip qualificat, amb una àmplia gamma d’instrumentació i recursos',
        alt: "Roseta d'ampolles Niskin suspesa sobre el mar des d'un vaixell"
      },
      marejada: {
        texto: 'Assessorament i solucions tècniques adaptades a les necessitats específiques',
        alt: 'Onada trencant en un mar agitat sota un cel de tempesta'
      },
      pelagia: {
        texto: 'Embarcació i suport logístic al litoral per a treballs científics',
        alt: 'Embarcació pneumàtica amb tècnics al costat d’una boia oceanogràfica groga davant de la costa de Barcelona'
      },
      reflejos: {
        texto: 'Innovar, desenvolupar, dissenyar, desplegar, implementar i personalitzar equips',
        alt: "Reflexos de llum sobre l'aigua i un fons de sorra"
      },
      fondeo: {
        texto: "Disseny i desplegament de fondejos instrumentats per a l'observació i la recollida de dades marines de manera continuada",
        alt: 'Fondeig oceanogràfic amb boies i instruments ancorat al fons marí'
      },
      rov: {
        texto: 'Integració de sensors en plataformes robòtiques per a mostrejos de precisió',
        alt: 'Vehicle submarí teledirigit (ROV) sobre un escull'
      },
      oficina: {
        texto: 'Eines i tècniques específiques de verificació per garantir la qualitat de les dades obtingudes en els estudis oceanogràfics.',
        alt: "Taula de treball amb plànols tècnics d'equips oceanogràfics i una placa electrònica"
      }
    },
    irADiapositiva: 'Anar a la diapositiva {n}',
    fichas: {
      memoria: 'Memòria anual',
      noticias: 'Notícies',
      equipo: 'Equip SIO'
    }
  },

  contacto: {
    titulo: 'CONTACTE I UBICACIÓ',
    info: 'Informació del SIO',
    direccion: 'Adreça',
    telefono: 'Telèfon',
    email: 'Correu electrònic',
    mapa: 'Mapa amb la ubicació del SIO',
    formTitulo: "Envia'ns la teva consulta",
    nombre: 'Nom',
    nombrePh: 'El teu nom',
    emailPh: "el.teu{'@'}correu.com",
    mensaje: 'Missatge',
    mensajePh: 'En què et podem ajudar?',
    trampa: 'No ho emplenis',
    privacidad: "Les dades d'aquest formulari només s'utilitzen per respondre la teva consulta i no se cedeixen a tercers. Responsable: Institut de Ciències del Mar (ICM-CSIC).",
    enviar: 'ENVIAR CONSULTA',
    enviando: 'ENVIANT…',
    enviado: 'Consulta enviada. Et respondrem al més aviat possible.',
    errorDatos: 'Revisa el nom, el correu i el missatge',
    errorLimite: 'Massa consultes. Torna-ho a provar més tard',
    errorEnvio: "No s'ha pogut enviar la consulta",
    errorConexion: "No s'ha pogut connectar amb el servidor",
    alternativa: 'Ens pots escriure directament a'
  },

  noEncontrado: {
    titulo: 'Pàgina no trobada',
    texto: "L'adreça que busques no existeix o ha canviat.",
    volver: "Tornar a l'inici"
  },

  servicios: {
    titulo: 'Els nostres serveis',
    subtitulo: 'Infraestructures i solucions tecnològiques per a la comunitat científica marina.',
    pelagia: {
      titulo: 'Embarcació Pelagia',
      texto: "Plataforma polivalent per a treballs d'oceanografia costanera, equipada per al desplegament d'instrumentació i mostreig.",
      items: ["Operacions de desplegament i recuperació d'equips.", 'Campanyes de mostreig biològic, geològic i fisicoquímic.', 'Gestió logística i tripulació especialitzada.']
    },
    instrumentacion: {
      titulo: 'Instrumentació',
      texto: "Accés a una àmplia gamma d'instrumentació oceanogràfica i suport tècnic per a la seva configuració.",
      items: ["Desenvolupament i personalització d'equips a mida.", 'Sistemes de comunicacions i telemetria submarina.', 'Manteniment preventiu i correctiu de sensors.']
    },
    tanques: {
      titulo: 'Tancs de proves',
      texto: "Lloguer d'àrees experimentals per a la validació i el calibratge d'instrumentació en entorns controlats.",
      items: ["Assajos d'estanquitat i flotabilitat per a robòtica.", 'Calibratge de sensors acústics i òptics.', "Suport d'enginyeria especialitzat durant els assajos."]
    },
    salinidad: {
      titulo: 'Anàlisi de salinitat',
      texto: "Servei de determinació precisa de la salinitat en mostres d'aigua de mar i calibratge amb salinòmetre.",
      items: ['Lectura de precisió amb Standard Seawater.', "Protocol estricte d'aclimatació de mostres.", 'Validació de dades de conductivitat CTD.']
    },
    fondeos: {
      titulo: 'Disseny i instal·lació de fondejos',
      texto: 'Planificació tècnica, integració de sensors i desplegament al mar de fondejos fixos i trípodes oceanogràfics.',
      items: ["Disseny i configuració d'ancoratges a mida.", "Integració i calibratge d'instruments.", 'Operacions de desplegament i seguiment continu.']
    },
    prototipado: {
      titulo: 'Prototipatge ràpid i fabricació',
      texto: "Disseny CAD avançat i producció de components mecànics complexos amb impressió 3D tècnica en materials d'alta resistència.",
      items: ['Modelatge 3D i disseny paramètric.', 'Impressió tècnica FDM i de resina.', 'Desenvolupament de carcasses submarines i adaptadors.']
    }
  },

  instrumentacion: {
    titulo: 'Instrumentació Oceanogràfica',
    subtitulo: 'Catàleg tècnic, calibratges i gestió de préstecs del SIO.',
    cargando: 'Connectant amb la base de dades del SIO...',
    errorCarga: "Error de connexió. No s'ha pogut carregar el catàleg d'instruments.",
    sinInstrumentos: 'No hi ha instruments catalogats en aquesta secció.',
    sinSubcategoria: 'Sense subcategoria',
    sinDescripcion: 'No hi ha descripció disponible.',
    sinParametros: 'No hi ha paràmetres tècnics.',
    verFicha: 'Veure la fitxa i reservar',
    ultimaCalibracion: 'Últim calibratge',
    verInfo: 'Veure informació tècnica i manuals',
    ocultarInfo: 'Amagar informació tècnica',
    descripcion: 'Descripció general',
    especificaciones: 'Especificacions tècniques / Manuals',
    paso1: 'Pas 1: Selecciona els dies de reserva',
    mesAnterior: 'Mes anterior',
    mesSiguiente: 'Mes següent',
    leyenda: '* Gris: Disponible | Blau: Ocupat | Verd: La teva selecció',
    paso2: 'Pas 2: Envia la sol·licitud',
    explicacion: "En prémer el botó s'obrirà el teu programa de correu amb la sol·licitud preparada per enviar a",
    explicacionFin: 'El SIO et respondrà per confirmar la reserva.',
    nombre: 'Nom i cognoms',
    nombrePh: 'Ex.: Eve Galimany Sanromà',
    institucion: 'Institució (opcional)',
    institucionPh: 'Ex.: ICATMAR',
    preparar: 'Preparar correu de sol·licitud',
    cerrar: 'Tancar detalls',
    prestamos: 'Préstecs SIO',
    ayuda: "Fes clic al nom de qualsevol instrument de l'esquerra per veure'n la fitxa tècnica completa i la disponibilitat.",
    comoFunciona: 'Com funciona?',
    pasos: ['Selecciona un instrument de la llista.', 'Fes clic als dies del calendari que necessitis.', "Escriu el teu nom i prem el botó: s'obrirà el teu correu amb la sol·licitud preparada.", 'Envia el correu i el SIO et respondrà per confirmar la reserva.'],
    faltanDatos: 'Selecciona almenys un dia i escriu el teu nom.',
    correo: {
      asunto: 'Sol·licitud de préstec SIO: {instrumento}',
      saludo: 'Hola, equip del SIO:',
      intro: "Voldria sol·licitar el préstec d'aquest instrument:",
      instrumento: 'Instrument',
      dias: 'Dies',
      diasValor: '{dias} ({mes})',
      nombre: 'Nom',
      institucion: 'Institució',
      despedida: "Quedo a l'espera de la vostra confirmació.\n\nSalutacions."
    }
  },

  pelagia: {
    titulo: 'Plataforma Pelagia',
    subtitulo: "Informació tècnica, disponibilitat i gestió de reserves de l'embarcació del SIO.",
    ficha: 'Fitxa tècnica',
    descripcionTitulo: 'Descripció general',
    descripcion: "La Pelagia és l'embarcació de treball costaner del Servei d'Enginyeria Oceanogràfica (SIO). Està dissenyada i equipada per donar suport a operacions de busseig científic, desplegament i recuperació d'instrumentació oceanogràfica i mostrejos costaners.",
    especificaciones: 'Especificacions principals',
    equipamiento: 'Equipament a bord',
    navegacion: 'Navegació',
    navegacionTexto: 'GPS / Sonda plotter integrada.',
    comunicacion: 'Comunicació',
    comunicacionTexto: 'Emissora VHF fixa.',
    maniobra: 'Maniobra',
    maniobraTexto: 'Pescant / Maquineta per a perfiladors lleugers (CTD, roseta petita).',
    seguridad: 'Seguretat',
    seguridadTexto: 'Material de seguretat complet.',
    normativaTitulo: "Normativa d'ús",
    normativa: "Per utilitzar l'embarcació Pelagia és estrictament obligatori comptar amb l'aprovació del SIO. La plataforma Pelagia està capitanejada per Brian Nicolás, professional amb àmplia experiència demostrable en navegació costanera i suport a operacions oceanogràfiques. El seu lideratge a bord garanteix la seguretat de la tripulació i la correcta execució dels protocols de treball marítim. El seu perfil resolutiu i la seva actitud col·laborativa faciliten enormement la coordinació de les activitats científiques durant les campanyes.",
    solicitud: "Sol·licitud d'ús",
    operativa: 'Operativa',
    paso1: 'Pas 1: Descarrega les normes i el pla de campanya.',
    descargar: 'Descarregar el Pla de Campanya',
    paso2: 'Pas 2: Selecciona els dies de sortida',
    mesAnterior: 'Mes anterior',
    mesSiguiente: 'Mes següent',
    leyenda: '* Gris: Disponible | Blau: Ocupat/Manteniment | Verd: La teva selecció',
    paso3: 'Pas 3: Envia el teu pla',
    explicacion: "En prémer el botó s'obrirà el teu programa de correu amb la sol·licitud preparada per enviar a",
    adjunta: 'Adjunta el Pla de Campanya signat',
    explicacionFin: "abans d'enviar-lo.",
    preparar: 'Preparar correu de sol·licitud',
    seleccionaDia: 'Selecciona almenys un dia',
    avisoDias: 'Selecciona almenys un dia al calendari de dalt per poder enviar.',
    correo: {
      asunto: 'Sol·licitud de sortida: Embarcació Pelagia',
      saludo: 'Hola, equip del SIO:',
      intro: "Voldria sol·licitar l'embarcació Pelagia per a aquests dies:",
      adjunto: 'Adjunto el Pla de Campanya signat.',
      despedida: "Quedo a l'espera de la vostra confirmació.\n\nSalutacions."
    }
  },

  tanques: {
    titulo: 'Tancs de proves',
    subtitulo: 'Instal·lacions experimentals per a assajos controlats, calibratge i biologia.',
    ficha: 'Fitxa tècnica',
    descripcionTitulo: 'Descripció general',
    descripcion: "El SIO disposa de tancs de proves d'alta capacitat dissenyats per al calibratge de sensors, assajos de fatiga de materials i simulacions de condicions marines controlades.",
    especificaciones: 'Especificacions principals',
    salinidad: 'Control de salinitat',
    salinidadTexto: 'Sistema automatitzat',
    iluminacion: 'Il·luminació',
    iluminacionTexto: 'Espectre regulable per a la fotosíntesi',
    filtracion: 'Filtració',
    filtracionTexto: 'Filtres UV i biològics integrats',
    solicitud: "Sol·licitud d'ús",
    operativa: 'OPERATIVA',
    paso1: 'Pas 1: Selecciona els dies',
    paso1Texto: 'Fes clic als dies disponibles (en blanc) del calendari que necessitis reservar.',
    mesAnterior: 'Mes anterior',
    mesSiguiente: 'Mes següent',
    paso2: 'Pas 2: Detalls de la sol·licitud',
    diasMarcados: 'Dies marcats',
    proposito: 'Finalitat de les proves',
    propositoPh: "Ex.: Calibratge de sensors d'oxigen PreSens...",
    grua: 'Faràs servir la grua de càrrega?',
    gruaNo: 'No, no caldrà',
    gruaSi: 'Sí, necessitarem la grua',
    enviar: 'PREPARAR CORREU DE SOL·LICITUD',
    faltanDatos: 'Selecciona almenys un dia al calendari i escriu la finalitat.',
    correo: {
      asunto: "Sol·licitud d'ús: Tancs de proves del SIO",
      saludo: 'Hola, equip del SIO:',
      intro: "Voldria sol·licitar l'ús dels tancs de proves.",
      dias: 'DIES SOL·LICITATS',
      proposito: 'FINALITAT DE LES PROVES',
      grua: 'ÚS DE LA GRUA DE CÀRREGA',
      gruaSi: 'Sí',
      gruaNo: 'No',
      despedida: "Quedo a l'espera de la vostra confirmació per coordinar-nos.\n\nSalutacions."
    }
  },

  salinidad: {
    titulo: 'Anàlisi de salinitat',
    subtitulo: "Determinació d'alta precisió per a mostres d'aigua de mar amb salinòmetre de laboratori.",
    ficha: 'Fitxa tècnica',
    descripcionTitulo: 'Descripció general',
    descripcion: "El Servei d'Enginyeria Oceanogràfica (SIO) ofereix l'anàlisi de salinitat de mostres d'aigua de mar. Aquest servei és fonamental per calibrar la conductivitat de les sondes CTD i garantir la màxima qualitat de les dades físiques.",
    especificaciones: 'Especificacions principals',
    equipo: 'Equip',
    equipoTexto: 'Salinòmetre Guildline Autosal 8400B',
    precision: 'Precisió',
    precisionTexto: 'Millor que 0,002 PSU',
    calibracion: 'Calibratge',
    calibracionTexto: 'IAPSO Standard Seawater',
    control: 'Control tèrmic',
    controlTexto: "Bany termostàtic d'alta estabilitat",
    solicitud: "Sol·licitud d'ús",
    operativa: 'OPERATIVA',
    explicacion: "Emplena les dades per coordinar l'anàlisi.",
    proyecto: 'Projecte i investigador principal (IP)',
    botellas: "Nombre d'ampolles necessàries",
    recogida: "Recollida d'ampolles",
    entrega: 'Lliurament de mostres',
    enviar: 'PREPARAR CORREU DE SOL·LICITUD',
    faltanDatos: 'Si us plau, emplena tots els camps.',
    correo: {
      asunto: "Sol·licitud d'anàlisi de salinitat: {proyecto}",
      saludo: 'Hola, equip del SIO:',
      intro: "Sol·licitud d'anàlisi de salinitat:",
      proyecto: 'Projecte',
      botellas: "Nombre d'ampolles",
      recogida: 'Recollida',
      entrega: 'Lliurament'
    }
  }
}
