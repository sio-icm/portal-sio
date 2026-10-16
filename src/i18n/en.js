export default {
  comun: {
    nombreServicio: 'Oceanographic Engineering Service',
    contacto: 'CONTACT',
    intranet: 'INTRANET',
    idiomas: 'Language',
    inicio: 'Home',
    menu: {
      sio: 'THE SIO',
      servicios: 'SERVICES',
      proyectos: 'PROJECTS',
      idi: 'R&D&I'
    },
    pie: '© 2026 Oceanographic Engineering Service - CSIC'
  },

  rutas: {
    servicios: 'Services',
    instrumentacion: 'Instrumentation',
    pelagia: 'Pelagia vessel',
    tanques: 'Test tanks',
    salinidad: 'Salinity analysis',
    fondeos: 'Moorings',
    prototipado: 'Prototyping',
    proyectos: 'Projects',
    idi: 'R&D&I',
    bluelab: 'BLUE Lab',
    equipo: 'Team',
    noticias: 'News',
    memoria: 'Annual report',
    contacto: 'Contact',
    intranet: 'Intranet',
    noEncontrado: 'Page not found'
  },

  inicio: {
    titulo: 'Oceanographic Engineering Service (SIO) · ICM-CSIC',
    carrusel: {
      peces: {
        texto: 'Specialised technical support for the marine sciences',
        alt: 'School of fish forming a sphere underwater'
      },
      niskin: {
        texto: 'A qualified team with a wide range of instrumentation and resources',
        alt: 'Rosette of Niskin bottles suspended over the sea from a ship'
      },
      marejada: {
        texto: 'Advice and technical solutions tailored to specific needs',
        alt: 'Wave breaking in a rough sea under a stormy sky'
      },
      pelagia: {
        texto: 'Coastal vessel and logistical support for scientific work',
        alt: 'Inflatable boat with technicians next to a yellow oceanographic buoy off the coast of Barcelona'
      },
      reflejos: {
        texto: 'Innovating, developing, designing, deploying, implementing and customising equipment',
        alt: 'Light reflections on the water over a sandy bottom'
      },
      fondeo: {
        texto: 'Design and deployment of instrumented moorings for continuous observation and collection of marine data',
        alt: 'Oceanographic mooring with buoys and instruments anchored to the seabed'
      },
      rov: {
        texto: 'Integration of sensors on robotic platforms for precision sampling',
        alt: 'Remotely operated underwater vehicle (ROV) over a reef'
      },
      oficina: {
        texto: 'Specific verification tools and techniques to ensure the quality of data from oceanographic studies.',
        alt: 'Workbench with technical drawings of oceanographic equipment and an electronics board'
      }
    },
    irADiapositiva: 'Go to slide {n}',
    fichas: {
      memoria: 'Annual report',
      noticias: 'News',
      equipo: 'SIO team'
    }
  },

  contacto: {
    titulo: 'CONTACT AND LOCATION',
    info: 'SIO information',
    direccion: 'Address',
    telefono: 'Phone',
    email: 'Email',
    mapa: 'Map showing the location of the SIO',
    formTitulo: 'Send us your enquiry',
    nombre: 'Name',
    nombrePh: 'Your name',
    emailPh: "your{'@'}email.com",
    mensaje: 'Message',
    mensajePh: 'How can we help you?',
    trampa: 'Do not fill in',
    privacidad: 'The data in this form is used only to answer your enquiry and is not shared with third parties. Data controller: Institut de Ciències del Mar (ICM-CSIC).',
    enviar: 'SEND ENQUIRY',
    enviando: 'SENDING…',
    enviado: 'Enquiry sent. We will get back to you as soon as possible.',
    errorDatos: 'Please check your name, email and message',
    errorLimite: 'Too many enquiries. Please try again later',
    errorEnvio: 'The enquiry could not be sent',
    errorConexion: 'Could not connect to the server',
    alternativa: 'You can also write to us directly at'
  },

  noEncontrado: {
    titulo: 'Page not found',
    texto: 'The address you are looking for does not exist or has changed.',
    volver: 'Back to home'
  },

  servicios: {
    titulo: 'Our Services',
    subtitulo: 'Infrastructure and technological solutions for the marine science community.',
    pelagia: {
      titulo: 'Pelagia vessel',
      texto: 'Multipurpose platform for coastal oceanography, equipped for deploying instruments and sampling.',
      items: ['Deployment and recovery of equipment.', 'Biological, geological and physico-chemical sampling campaigns.', 'Logistics management and specialised crew.']
    },
    instrumentacion: {
      titulo: 'Instrumentation',
      texto: 'Access to a wide range of oceanographic instruments and technical support for their configuration.',
      items: ['Development and customisation of bespoke equipment.', 'Underwater communication and telemetry systems.', 'Preventive and corrective sensor maintenance.']
    },
    tanques: {
      titulo: 'Test Tanks',
      texto: 'Rental of experimental areas for validating and calibrating instruments in controlled environments.',
      items: ['Watertightness and buoyancy tests for robotics.', 'Calibration of acoustic and optical sensors.', 'Specialised engineering support during tests.']
    },
    salinidad: {
      titulo: 'Salinity Analysis',
      texto: 'Precise salinity determination in seawater samples and calibration with a salinometer.',
      items: ['Precision readings with Standard Seawater.', 'Strict sample acclimatisation protocol.', 'Validation of CTD conductivity data.']
    },
    fondeos: {
      titulo: 'Mooring Design and Installation',
      texto: 'Technical planning, sensor integration and at-sea deployment of fixed moorings and oceanographic tripods.',
      items: ['Design and configuration of bespoke anchoring systems.', 'Instrument integration and calibration.', 'Deployment operations and continuous monitoring.']
    },
    prototipado: {
      titulo: 'Rapid Prototyping and Manufacturing',
      texto: 'Advanced CAD design and production of complex mechanical components using technical 3D printing in high-strength materials.',
      items: ['3D modelling and parametric design.', 'Technical FDM and resin printing.', 'Development of underwater housings and adapters.']
    }
  },

  instrumentacion: {
    titulo: 'Oceanographic Instrumentation',
    subtitulo: 'Technical catalogue, calibrations and SIO equipment loans.',
    cargando: 'Connecting to the SIO database...',
    errorCarga: 'Connection error. The instrument catalogue could not be loaded.',
    sinInstrumentos: 'There are no instruments listed in this section.',
    sinSubcategoria: 'No subcategory',
    sinDescripcion: 'No description available.',
    sinParametros: 'No technical parameters.',
    verFicha: 'View details and book',
    ultimaCalibracion: 'Last calibration',
    verInfo: 'View technical information and manuals',
    ocultarInfo: 'Hide technical information',
    descripcion: 'General description',
    especificaciones: 'Technical specifications / Manuals',
    paso1: 'Step 1: Select the days you need',
    mesAnterior: 'Previous month',
    mesSiguiente: 'Next month',
    leyenda: '* Grey: Available | Blue: Booked | Green: Your selection',
    paso2: 'Step 2: Send the request',
    explicacion: 'When you press the button, your email program will open with the request ready to send to',
    explicacionFin: 'The SIO will reply to confirm the booking.',
    nombre: 'Full name',
    nombrePh: 'E.g. Eve Galimany Sanromà',
    institucion: 'Institution (optional)',
    institucionPh: 'E.g. ICATMAR',
    preparar: 'Prepare request email',
    cerrar: 'Close details',
    prestamos: 'SIO equipment loans',
    ayuda: 'Click the name of any instrument on the left to see its full technical sheet and availability.',
    comoFunciona: 'How does it work?',
    pasos: ['Select an instrument from the list.', 'Click the days you need on the calendar.', 'Enter your name and press the button: your email will open with the request ready.', 'Send the email and the SIO will reply to confirm the booking.'],
    faltanDatos: 'Select at least one day and enter your name.',
    correo: {
      asunto: 'SIO equipment loan request: {instrumento}',
      saludo: 'Hello SIO team,',
      intro: 'I would like to request the loan of this instrument:',
      instrumento: 'Instrument',
      dias: 'Days',
      diasValor: '{dias} ({mes})',
      nombre: 'Name',
      institucion: 'Institution',
      despedida: 'I look forward to your confirmation.\n\nBest regards.'
    }
  },

  pelagia: {
    titulo: 'Pelagia Platform',
    subtitulo: 'Technical information, availability and booking of the SIO vessel.',
    ficha: 'Technical Sheet',
    descripcionTitulo: 'General Description',
    descripcion: 'Pelagia is the coastal work vessel of the Oceanographic Engineering Service (SIO). It is designed and equipped to support scientific diving, the deployment and recovery of oceanographic instruments, and coastal sampling.',
    especificaciones: 'Main Specifications',
    equipamiento: 'On-board equipment',
    navegacion: 'Navigation',
    navegacionTexto: 'GPS / integrated chart plotter and sounder.',
    comunicacion: 'Communication',
    comunicacionTexto: 'Fixed VHF radio.',
    maniobra: 'Handling',
    maniobraTexto: 'Davit / winch for light profilers (CTD, small rosette).',
    seguridad: 'Safety',
    seguridadTexto: 'Full safety equipment.',
    normativaTitulo: 'Rules of Use',
    normativa: 'Use of the Pelagia vessel strictly requires approval from the SIO. Pelagia is captained by Brian Nicolás, a professional with extensive, proven experience in coastal navigation and in supporting oceanographic operations. His leadership on board ensures the safety of the crew and the correct execution of maritime work protocols. His problem-solving approach and collaborative attitude greatly ease the coordination of scientific activities during campaigns.',
    solicitud: 'Booking Request',
    operativa: 'Operational',
    paso1: 'Step 1: Download the rules and campaign plan.',
    descargar: 'Download Campaign Plan',
    paso2: 'Step 2: Select the days you want to go out',
    mesAnterior: 'Previous month',
    mesSiguiente: 'Next month',
    leyenda: '* Grey: Available | Blue: Booked/Maintenance | Green: Your selection',
    paso3: 'Step 3: Send your plan',
    explicacion: 'When you press the button, your email program will open with the request ready to send to',
    adjunta: 'Attach the signed Campaign Plan',
    explicacionFin: 'before sending it.',
    preparar: 'Prepare request email',
    seleccionaDia: 'Select at least one day',
    avisoDias: 'Select at least one day in the calendar above to be able to send.',
    correo: {
      asunto: 'Trip request: Pelagia vessel',
      saludo: 'Hello SIO team,',
      intro: 'I would like to request the Pelagia vessel for these days:',
      adjunto: 'Please find the signed Campaign Plan attached.',
      despedida: 'I look forward to your confirmation.\n\nBest regards.'
    }
  },

  tanques: {
    titulo: 'Test Tanks',
    subtitulo: 'Experimental facilities for controlled tests, calibration and biology.',
    ficha: 'Technical Sheet',
    descripcionTitulo: 'General Description',
    descripcion: 'The SIO has high-capacity test tanks designed for sensor calibration, material fatigue tests and simulations of controlled marine conditions.',
    especificaciones: 'Main Specifications',
    salinidad: 'Salinity control',
    salinidadTexto: 'Automated system',
    iluminacion: 'Lighting',
    iluminacionTexto: 'Adjustable spectrum for photosynthesis',
    filtracion: 'Filtration',
    filtracionTexto: 'Integrated UV and biological filters',
    solicitud: 'Booking Request',
    operativa: 'OPERATIONAL',
    paso1: 'Step 1: Select the days',
    paso1Texto: 'Click the available days (in white) that you need to book.',
    mesAnterior: 'Previous month',
    mesSiguiente: 'Next month',
    paso2: 'Step 2: Request details',
    diasMarcados: 'Selected days',
    proposito: 'Purpose of the tests',
    propositoPh: 'E.g. Calibration of PreSens oxygen sensors...',
    grua: 'Will you use the loading crane?',
    gruaNo: 'No, it will not be needed',
    gruaSi: 'Yes, we will need the crane',
    enviar: 'PREPARE REQUEST EMAIL',
    faltanDatos: 'Select at least one day in the calendar and describe the purpose.',
    correo: {
      asunto: 'Booking request: SIO Test Tanks',
      saludo: 'Hello SIO team,',
      intro: 'I would like to request the use of the Test Tanks.',
      dias: 'REQUESTED DAYS',
      proposito: 'PURPOSE OF THE TESTS',
      grua: 'USE OF THE LOADING CRANE',
      gruaSi: 'Yes',
      gruaNo: 'No',
      despedida: 'I look forward to your confirmation so we can coordinate.\n\nBest regards.'
    }
  },

  salinidad: {
    titulo: 'Salinity Analysis',
    subtitulo: 'High-precision determination for seawater samples using a laboratory salinometer.',
    ficha: 'Technical Sheet',
    descripcionTitulo: 'General Description',
    descripcion: 'The Oceanographic Engineering Service (SIO) offers salinity analysis of seawater samples. This service is essential for calibrating the conductivity of CTD probes and ensuring the highest quality of physical data.',
    especificaciones: 'Main Specifications',
    equipo: 'Equipment',
    equipoTexto: 'Guildline Autosal 8400B salinometer',
    precision: 'Accuracy',
    precisionTexto: 'Better than 0.002 PSU',
    calibracion: 'Calibration',
    calibracionTexto: 'IAPSO Standard Seawater',
    control: 'Temperature control',
    controlTexto: 'High-stability thermostatic bath',
    solicitud: 'Service Request',
    operativa: 'OPERATIONAL',
    explicacion: 'Fill in the details so we can arrange the analysis.',
    proyecto: 'Project and Principal Investigator (PI)',
    botellas: 'Number of bottles needed',
    recogida: 'Bottle collection',
    entrega: 'Sample delivery',
    enviar: 'PREPARE REQUEST EMAIL',
    faltanDatos: 'Please fill in all the fields.',
    correo: {
      asunto: 'Salinity analysis request: {proyecto}',
      saludo: 'Hello SIO team,',
      intro: 'Salinity analysis request:',
      proyecto: 'Project',
      botellas: 'Number of bottles',
      recogida: 'Collection',
      entrega: 'Delivery'
    }
  },

  fondeos: {
    titulo: 'Oceanographic Mooring Management',
    subtitulo: 'Technical planning, design, installation and monitoring of instrumented moorings and tripods.',
    intro: 'The Oceanographic Engineering Service takes part in the design, preparation and installation of instrumented oceanographic moorings and tripods. We handle the full technical planning, making sure every component is optimal for obtaining high-quality data in your oceanographic studies.',
    nota: 'Note: The instruments and auxiliary equipment required for each type of study are to be provided by the user.',
    fasesTitulo: 'Service Phases',
    fases: [
      { titulo: 'Design', texto: 'Analysis of scientific needs and optimal mooring configuration.' },
      { titulo: 'Preparation', texto: 'Integration, instrument calibration and component assembly.' },
      { titulo: 'Deployment', texto: 'Field installation by a specialised, expert team.' },
      { titulo: 'Monitoring', texto: 'Continuous control and monitoring of the mooring while in operation.' }
    ],
    instrumentosTitulo: 'Integrable Instrumentation',
    instrumentosTexto: 'Our systems can integrate a wide variety of sensors depending on the parameters you need to measure:',
    instrumentos: [
      { nombre: 'Current meters and Doppler profilers', texto: 'Current speeds and directions' },
      { nombre: 'Temperature sensors', texto: 'Water temperature monitoring' },
      { nombre: 'Conductivity sensors', texto: 'Salinity measurement' },
      { nombre: 'Pressure sensors', texto: 'Depth determination' },
      { nombre: 'Turbidity meters', texto: 'Particle concentration and turbidity' },
      { nombre: 'Oxygen sensors', texto: 'Dissolved oxygen in the water' },
      { nombre: 'Fluorometers', texto: 'Chlorophyll and organic matter' },
      { nombre: 'pH sensors', texto: 'Acidity and alkalinity' },
      { nombre: 'Turbulence sensors', texto: 'Characterisation of turbulent processes' },
      { nombre: 'Sediment traps', texto: 'Collection of suspended particles' }
    ],
    solicitarTitulo: 'Request a Mooring Installation',
    proyecto: 'Project name / Principal Investigator',
    inicio: 'Planned start date',
    retirada: 'Planned recovery date',
    descripcion: 'Campaign description',
    descripcionPh: 'Brief description of the campaign, its objectives and the instruments you will provide...',
    avisoCorreo: 'When you press the button, your email program will open with the request ready to send to',
    enviar: 'Prepare request email',
    estadoTitulo: 'Current Mooring Status',
    activos: 'Active at sea',
    retirados: 'Recovered / History',
    ip: 'PI',
    correo: {
      asunto: 'Mooring installation request: {proyecto}',
      saludo: 'Hello SIO team,',
      intro: 'I would like to request the installation of a mooring.',
      proyecto: 'Project / PI',
      inicio: 'Planned start date',
      retirada: 'Planned recovery date',
      despedida: 'I look forward to hearing from you.\n\nBest regards.'
    }
  },

  prototipado: {
    titulo: 'Rapid Prototyping and Manufacturing',
    subtitulo: 'Advanced CAD design, precision machining and production of complex mechanical components.',
    intro: 'The Oceanographic Engineering Service has advanced manufacturing and rapid prototyping capabilities to directly support marine research. Starting from CAD design, we create bespoke parts.',
    capacidadesTitulo: 'Workshop Capabilities',
    capacidades: [
      { titulo: 'Technical 3D Printing', texto: 'Additive manufacturing in high-performance materials (technical resins, advanced filaments).' },
      { titulo: 'CAD / CAE Design', texto: 'Parametric 3D modelling and validation of complex geometries for underwater environments.' }
    ],
    solicitarTitulo: 'Request a Part or Prototype',
    proyecto: 'Project name / Principal Investigator',
    pieza: 'Type of part or component',
    piezaPh: 'Type of part or component needed (e.g. watertight housing, sensor mount...)',
    requisitos: 'Technical requirements',
    requisitosPh: 'Describe the technical requirements, approximate dimensions or intended material...',
    avisoCorreo: 'When you press the button, your email program will open with the request ready to send to',
    enviar: 'Prepare request email',
    correo: {
      asunto: 'Part or prototype request: {pieza}',
      saludo: 'Hello SIO team,',
      intro: 'I would like to request the manufacture of a part or prototype.',
      proyecto: 'Project / PI',
      pieza: 'Part or component',
      despedida: 'I look forward to hearing from you.\n\nBest regards.'
    }
  },

  proyectos: {
    titulo: 'Projects and Campaigns',
    subtitulo: 'See the current status of the service’s technical projects and ongoing requests.',
    cargando: 'Loading projects...',
    errorCarga: 'The projects could not be loaded.',
    vacio: 'There are no projects at this stage.',
    detalle: 'Show details',
    ocultarDetalle: 'Hide details',
    grupos: {
      enCurso: { titulo: 'In Progress', texto: 'Activities and campaigns currently being carried out.' },
      aprobados: { titulo: 'Approved', texto: 'Confirmed projects awaiting technical start.' },
      solicitados: { titulo: 'Requested', texto: 'Proposals under evaluation.' },
      finalizados: { titulo: 'Completed', texto: 'Archive of completed campaigns and projects.' }
    },
    categorias: {
      infraestructura: 'Infrastructure',
      contrato: 'Contract',
      planNacional: 'National Plan',
      idi: 'R&D&I',
      divulgacion: 'Science outreach',
      otro: 'Other'
    }
  },

  idi: {
    titulo: 'R&D&I',
    subtitulo: 'Driving marine technological innovation and knowledge transfer at the SIO.',
    oficina: 'R&D&I Office',
    oficinaTexto: 'Comprehensive research support: from managing funding calls to protecting results and technology transfer.',
    items: ['Project management and specialised technical advice.', 'Intellectual property and valorisation of the technology we develop.', 'Promoting collaboration with companies and centres in the marine sector.'],
    invitacion: 'At the SIO we believe in co-creation. If you have a technical need for your campaigns, an idea for a new sensor, or want to adapt robotics to an extreme environment,',
    invitacionDestacado: 'we want to hear from you',
    nombre: 'Full name',
    nombrePh: 'E.g. Dr Elena Martínez',
    departamento: 'Institution / Department',
    departamentoPh: 'E.g. Dept. of Physical Oceanography',
    reto: 'What is the oceanographic challenge or idea?',
    retoPh: 'Briefly describe what you need to measure, the technical problem you have, or the technology you would like to explore.',
    entorno: 'Intended application environment',
    entornos: {
      costa: 'Coastal zone / Shallow waters',
      pelagico: 'Open sea / Continental shelf',
      profundo: 'Deep waters / Benthos',
      laboratorio: 'Laboratory tests / Tank',
      otro: 'Other'
    },
    avisoCorreo: 'When you press the button, your email program will open with the proposal ready to send to',
    enviar: 'Prepare proposal email',
    correo: {
      asunto: 'R&D&I proposal: {nombre}',
      saludo: 'Hello SIO team,',
      nombre: 'Name',
      departamento: 'Institution / Department',
      entorno: 'Application environment',
      despedida: 'Best regards.'
    }
  },

  bluelab: {
    lema: 'Pioneering the future of marine observation',
    lineasTitulo: 'Innovation Lines',
    lineas: [
      { titulo: 'Autonomous Platforms', texto: 'Adaptive sampling and fleet coordination using AUVs, ASVs and gliders. We operate as real-time communication nodes for coastal and ocean mapping.' },
      { titulo: 'Bio-inspired Robotics', texto: 'Design of legged benthic vehicles (crawlers) that interact with the seabed while minimising environmental disturbance and acoustic footprint.' },
      { titulo: 'Biologging', texto: 'Using marine megafauna (birds, turtles, sharks) fitted with advanced sensors as in situ observation platforms in highly dynamic areas.' },
      { titulo: 'Machine Learning & AI', texto: 'Multi-agent reinforcement learning (MARL) algorithms, edge computing for in situ image classification, and automated big data processing.' }
    ],
    flotaTitulo: 'Our Fleet and Infrastructure',
    flota: [
      {
        titulo: 'Surface Vehicles (ASVs)',
        items: [
          { nombre: 'Coastal ASVs (~1 m)', texto: 'Two SEABOTS SB100 PRO units. Equipped with NORBIT echo sounders and CTD, ideal for very shallow coastal bathymetry and rapid deployments.' },
          { nombre: 'Ocean ASVs (long-range)', texto: 'Long-endurance platforms powered by solar and wave energy, with satellite communication and acoustic modems for open-sea missions.' }
        ]
      },
      {
        titulo: 'Manufacturing and Test Workshop',
        items: [
          { nombre: 'Rapid Manufacturing', texto: 'Advanced 3D printing facility, including large-format and resin systems (Creality K2 Plus Combo), a milling machine and precision tools for developing and customising robotic components and underwater housings.' }
        ]
      }
    ],
    proyectosTitulo: 'Featured Projects',
    proyectos: [
      { nombre: 'DIGI4ECO', texto: 'Pioneering European initiative to create a Digital Twin of the Ocean.' },
      { nombre: 'TECTUGA', texto: 'Attaching devices to sea turtles and coordinating with ASVs to study their behaviour.' },
      { nombre: 'AVALON & MERLIN', texto: 'Underwater optical communications and advances in cooperative marine robotics.' }
    ],
    equipoTitulo: 'The Team',
    liderazgo: 'Scientific Leadership',
    equipoSio: 'SIO Team',
    predoctorales: 'Predoctoral Researchers'
  }
}
