import { useEffect, useRef } from 'react'
import { useParams } from 'react-router-dom'
import { getDocument, GlobalWorkerOptions } from 'pdfjs-dist'

GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/pdf.worker.min.js`

export default function DocumentDetail() {
  const { id } = useParams()
  const canvasRef = useRef(null)

  useEffect(() => {
    const url = `/sample.pdf`
    getDocument(url).promise.then(pdf => {
      pdf.getPage(1).then(page => {
        const viewport = page.getViewport({ scale: 1 })
        const canvas = canvasRef.current
        const context = canvas.getContext('2d')
        canvas.height = viewport.height
        canvas.width = viewport.width
        page.render({ canvasContext: context, viewport })
      })
    })
  }, [id])

  return (
    <div className="p-4">
      <canvas ref={canvasRef}></canvas>
    </div>
  )
}
