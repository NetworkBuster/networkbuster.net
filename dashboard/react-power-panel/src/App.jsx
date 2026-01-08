import React from 'react'
import PowerPanel from './PowerPanel'

export default function App(){
  return (
    <div style={{padding:20,fontFamily:'Inter,Segoe UI,Arial'}}>
      <h1>NetworkBuster — Power Panel (React)</h1>
      <PowerPanel wsUrl={process.env.WS_URL || 'ws://localhost:8765'} />
    </div>
  )
}
