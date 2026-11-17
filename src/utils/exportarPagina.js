import { limpiarHtml } from './limpiarHtml'

// Descàrrega d'una pàgina de documentació en diversos formats (PDF per defecte).
// L'HTML de l'editor (Quill 2) es normalitza abans: llistes de punts com a <ul> i
// blocs de codi com a <pre>, perquè es vegin bé fora de la web (Word, Markdown...).

const ESTILOS = `
  body { font-family: Arial, Helvetica, sans-serif; color: #222; line-height: 1.55; font-size: 11pt; }
  h1 { color: #012169; font-size: 20pt; margin: 0 0 4pt; }
  h2 { color: #012169; font-size: 15pt; margin: 16pt 0 6pt; }
  h3 { color: #012169; font-size: 12.5pt; margin: 12pt 0 4pt; }
  .meta { color: #666; font-size: 9pt; margin: 0 0 14pt; }
  pre { background: #f2f4f7; border: 1px solid #d8dde3; padding: 8pt; font-family: 'Courier New', monospace; font-size: 9.5pt; white-space: pre-wrap; }
  blockquote { border-left: 3pt solid #8cc63f; margin: 0 0 8pt; padding: 4pt 10pt; background: #f6faf0; }
  img { max-width: 100%; height: auto; }
  table { border-collapse: collapse; } td, th { border: 1px solid #ccc; padding: 4pt 6pt; }
  a { color: #0086c0; }
`

const escapar = (s) => String(s || '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]))

// Quill 2 -> HTML estàndard (també el fa servir l'editor per obrir pàgines antigues)
export const normalizarHtml = (html, { exportar = false } = {}) => {
  const doc = new DOMParser().parseFromString(`<div>${limpiarHtml(html)}</div>`, 'text/html')
  const raiz = doc.body.firstChild
  raiz.querySelectorAll('.ql-ui').forEach(n => n.remove())
  // Blocs de codi: <div class="ql-code-block-container"><div class="ql-code-block">línia</div>... -> <pre>
  raiz.querySelectorAll('.ql-code-block-container').forEach(c => {
    const pre = doc.createElement('pre')
    pre.textContent = [...c.querySelectorAll('.ql-code-block')].map(l => l.textContent).join('\n')
    c.replaceWith(pre)
  })
  // Llistes: <ol><li data-list="bullet"> -> <ul><li>
  raiz.querySelectorAll('ol').forEach(ol => {
    const items = [...ol.children]
    if (items.length && items.every(li => li.getAttribute('data-list') === 'bullet')) {
      const ul = doc.createElement('ul')
      items.forEach(li => { li.removeAttribute('data-list'); ul.appendChild(li) })
      ol.replaceWith(ul)
    } else items.forEach(li => li.removeAttribute('data-list'))
  })
  // Tasques (editor nou): en exportar, la casella es converteix en ☑ / ☐ (en editar es mantenen)
  if (exportar) raiz.querySelectorAll('ul[data-type="taskList"] > li').forEach(li => {
    li.querySelector(':scope > label')?.remove()
    li.prepend(li.getAttribute('data-checked') === 'true' ? '☑ ' : '☐ ')
  })
  // Paràgrafs buits de l'editor (<p><br></p>)
  raiz.querySelectorAll('p').forEach(p => { if (p.innerHTML === '<br>') p.remove() })
  return raiz.innerHTML
}

const nombreArchivo = (titulo, ext) => (titulo || 'pagina').normalize('NFD').replace(/[̀-ͯ]/g, '')
  .replace(/[^\w\- ]+/g, '').trim().replace(/\s+/g, '_').slice(0, 80) + '.' + ext

const descargar = (contenido, tipo, nombre) => {
  const url = URL.createObjectURL(contenido instanceof Blob ? contenido : new Blob([contenido], { type: tipo }))
  const a = document.createElement('a')
  a.href = url; a.download = nombre
  document.body.appendChild(a); a.click(); a.remove()
  setTimeout(() => URL.revokeObjectURL(url), 2000)
}

// Cos comú: títol, dades i contingut; els adjunts, com a llista d'enllaços
const cuerpoHtml = (pagina, textos) => {
  const origen = window.location.origin
  const adjuntos = (pagina.adjuntos || []).length
    ? `<h2>${escapar(textos.adjuntos)}</h2><ul>${pagina.adjuntos.map(a =>
      `<li><a href="${escapar(origen + a.href)}">${escapar(a.nombre)}</a> (${escapar(a.formato)})</li>`).join('')}</ul>`
    : ''
  return `<h1>${escapar(pagina.titulo)}</h1>
<p class="meta">${escapar(textos.meta)}</p>
${normalizarHtml(pagina.contenido, { exportar: true })}
${adjuntos}`
}

const documentoHtml = (pagina, textos, extraHead = '') => `<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>${escapar(pagina.titulo)}</title>${extraHead}<style>${ESTILOS}</style></head>
<body>${cuerpoHtml(pagina, textos)}</body></html>`

export const FORMATOS = ['pdf', 'docx', 'html', 'md', 'txt']

export const exportarPagina = async (pagina, formato, textos) => {
  if (formato === 'html') {
    return descargar(documentoHtml(pagina, textos), 'text/html;charset=utf-8', nombreArchivo(pagina.titulo, 'html'))
  }
  if (formato === 'docx') {
    // Word obre directament aquest HTML (.doc) i el pot desar com a .docx
    const head = '<meta name="ProgId" content="Word.Document"><meta name="Generator" content="SIO">'
    const html = documentoHtml(pagina, textos, head)
      .replace('<html>', '<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word" xmlns="http://www.w3.org/TR/REC-html40">')
    return descargar('﻿' + html, 'application/msword', nombreArchivo(pagina.titulo, 'doc'))
  }
  if (formato === 'md') {
    const { default: TurndownService } = await import('turndown')
    const td = new TurndownService({ headingStyle: 'atx', codeBlockStyle: 'fenced', bulletListMarker: '-' })
    return descargar(td.turndown(cuerpoHtml(pagina, textos)) + '\n', 'text/markdown;charset=utf-8', nombreArchivo(pagina.titulo, 'md'))
  }
  if (formato === 'txt') {
    const div = document.createElement('div')
    div.innerHTML = cuerpoHtml(pagina, textos)
    div.querySelectorAll('li').forEach(li => li.prepend('• '))
    div.querySelectorAll('h1, h2, h3, p, li, pre, blockquote').forEach(el => el.append('\n'))
    return descargar(div.textContent.replace(/\n{3,}/g, '\n\n').trim() + '\n', 'text/plain;charset=utf-8', nombreArchivo(pagina.titulo, 'txt'))
  }
  // PDF (per defecte): es dibuixa la pàgina en un full A4 i es descarrega
  const [{ jsPDF }, { default: html2canvas }] = await Promise.all([import('jspdf'), import('html2canvas')])
  window.html2canvas = html2canvas
  const caja = document.createElement('div')
  caja.style.cssText = 'position:fixed;left:-10000px;top:0;width:700px;background:white;padding:0'
  // Els estils només s'apliquen dins de la caixa (.exp-pdf), no a la resta de la pàgina
  const estilos = ESTILOS.replace(/(^|\})\s*([^{}]+)\{/g, (m, fin, sel) =>
    `${fin} ${sel.split(',').map(x => x.trim() === 'body' ? '.exp-pdf' : '.exp-pdf ' + x.trim()).join(', ')} {`)
  caja.innerHTML = `<style>${estilos}</style><div class="exp-pdf">${cuerpoHtml(pagina, textos)}</div>`
  document.body.appendChild(caja)
  try {
    const pdf = new jsPDF({ unit: 'pt', format: 'a4' })
    await pdf.html(caja, {
      x: 40, y: 40, width: 515, windowWidth: 700, autoPaging: 'text',
      margin: [40, 40, 40, 40], html2canvas: { useCORS: true }
    })
    pdf.save(nombreArchivo(pagina.titulo, 'pdf'))
  } finally {
    caja.remove()
  }
}
