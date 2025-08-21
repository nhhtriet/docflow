import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

export default function DocumentList() {
  const [docs, setDocs] = useState([])
  useEffect(() => {
    fetch('/documents')
      .then(res => res.json())
      .then(setDocs)
  }, [])

  return (
    <div className="p-4">
      <h1 className="text-2xl mb-4">Documents</h1>
      <ul className="space-y-2">
        {docs.map(doc => (
          <li key={doc.id}>
            <Link className="text-blue-600" to={`/documents/${doc.id}`}>{doc.title}</Link>
          </li>
        ))}
      </ul>
    </div>
  )
}
