import React, {useEffect, useState, useRef} from 'react'
import { Line } from 'react-chartjs-2'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js'
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)

export default function PowerPanel({wsUrl}){
  const [telemetry, setTelemetry] = useState(null)
  const [connected, setConnected] = useState(false)
  const wsRef = useRef(null)
  const historyRef = useRef({harvest: [], battery: [], ts: []})

  useEffect(()=>{
    const ws = new WebSocket(wsUrl)
    ws.onopen = ()=>{ setConnected(true) }
    ws.onmessage = (m)=>{
      try {
        const d = JSON.parse(m.data)
        const t = d.telemetry || d
        setTelemetry(t)
        // update history
        historyRef.current.harvest.push(t.harvest_mw || 0)
        historyRef.current.battery.push(t.batteryPercent || 0)
        historyRef.current.ts.push(new Date((t.ts||Date.now())*1000).toLocaleTimeString())
        if(historyRef.current.harvest.length > 60){
          historyRef.current.harvest.shift()
          historyRef.current.battery.shift()
          historyRef.current.ts.shift()
        }
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
  const chartData = {
    labels: historyRef.current.ts,
    datasets: [
      { label: 'Harvest (mW)', data: historyRef.current.harvest, borderColor: '#0f9', backgroundColor: 'rgba(15,153,51,0.2)', tension: 0.3 },
      { label: 'Battery %', data: historyRef.current.battery, borderColor: '#09f', backgroundColor: 'rgba(9,120,255,0.15)', tension: 0.3, yAxisID: 'y2' }
    ]
  }
  const chartOpts = {
    responsive: true,
    interaction: { mode: 'index', intersect: false },
    scales: {
      y: { beginAtZero: true },
      y2: { position: 'right', beginAtZero: true, max: 100 }
    }
  }

  return (
    <div>
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

      <div style={{marginTop:16}}>
        <Line data={chartData} options={chartOpts} />
      </div>
    </div>
  )
}
