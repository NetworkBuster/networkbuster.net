import React, {useEffect, useState, useRef} from 'react'

export default function PowerPanel({wsUrl}){
  const [telemetry, setTelemetry] = useState(null)
  const [connected, setConnected] = useState(false)
  const wsRef = useRef(null)

  useEffect(()=>{
    const ws = new WebSocket(wsUrl)
    ws.onopen = ()=>{ setConnected(true) }
    ws.onmessage = (m)=>{
      try {
        const d = JSON.parse(m.data)
        const t = d.telemetry || d
        setTelemetry(t)
      } catch(e){ console.warn('bad msg', e) }
    }
    ws.onclose = ()=>{ setConnected(false); setTimeout(()=>connect(), 2000) }
    wsRef.current = ws
    function connect(){ if(wsRef.current && wsRef.current.readyState === WebSocket.CLOSED){ wsRef.current = new WebSocket(wsUrl) } }
    return ()=>{ try{ ws.close() }catch(e){} }
  }, [wsUrl])

  function sendControl(payload){
    // in production use secure control channel / auth
    if(wsRef.current && wsRef.current.readyState===WebSocket.OPEN){
      wsRef.current.send(JSON.stringify({control:payload}))
    }
  }

  const pct = telemetry ? telemetry.batteryPercent : 0
  return (
    <div style={{display:'flex',gap:20,alignItems:'center'}}>
      <div style={{width:160,height:160,borderRadius:80,display:'flex',alignItems:'center',justifyContent:'center',background:`conic-gradient(#0f9 0 ${pct}%, #eee ${pct}% 100%)`,fontSize:20}}>{pct}%</div>
      <div style={{flex:1}}>
        <div>Harvest: <strong>{telemetry ? telemetry.harvest_mw : '--'} mW</strong></div>
        <div>Mode: <strong>{telemetry ? telemetry.mode : '-'}</strong></div>
        <div>Queued: <strong>{telemetry ? telemetry.queued : 0}</strong></div>
        <div>Sent total: <strong>{telemetry && telemetry.stats ? telemetry.stats.sent : 0}</strong></div>
        <div>Uptime: <strong>{telemetry ? telemetry.uptime_s : 0}s</strong></div>
        <div style={{marginTop:8}}>
          <button onClick={()=>sendControl({set_mode:'low_power'})}>Set Low Power</button>
          <button onClick={()=>sendControl({set_mode:'normal'})} style={{marginLeft:8}}>Set Normal</button>
          <span style={{marginLeft:16,color: connected ? 'green' : '#999' }}>{connected? 'Connected':'Disconnected'}</span>
        </div>
      </div>
    </div>
  )
}
