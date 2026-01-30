// Layout persistence: try server-side POST to /api/dashboard/layout, fallback to localStorage
export async function saveLayout(layout){
  try{
    const res = await fetch('/api/dashboard/layout',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(layout)});
    if (!res.ok) throw new Error('server save failed');
    return {source:'server'};
  }catch(e){
    try{
      localStorage.setItem('dashboard-layout-v1', JSON.stringify(layout));
      return {source:'local'};
    }catch(e2){
      console.error('Failed to save layout',e2);
      throw e2;
    }
  }
}

export async function loadLayout(){
  try{
    const res = await fetch('/api/dashboard/layout');
    if (res.ok){
      const data = await res.json();
      return data;
    }
  }catch(e){
    // ignore
  }
  const raw = localStorage.getItem('dashboard-layout-v1');
  return raw ? JSON.parse(raw) : null;
}
