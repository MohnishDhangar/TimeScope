import {useEffect,useRef,useState} from 'react'
type Props={src:string;date:string;smooth:boolean;zoom:number;pan:{x:number;y:number};onPan:(p:{x:number;y:number})=>void;fov:number;label:string;onSize?:(size:number)=>void}
export default function SkyFrame({src,date,smooth,zoom,pan,onPan,fov,label,onSize}:Props){
 const box=useRef<HTMLDivElement>(null),drag=useRef<{x:number;y:number}|null>(null)
 const [side,setSide]=useState(1)
 useEffect(()=>{const o=new ResizeObserver(([entry])=>setSide(Math.min(entry.contentRect.width,entry.contentRect.height)*.95));if(box.current)o.observe(box.current);return()=>o.disconnect()},[])
 const barArcmin=fov/(zoom*5),barPixels=side/5
 return <div ref={box} className="imagebox" onPointerDown={e=>{drag.current={x:e.clientX/side-pan.x,y:e.clientY/side-pan.y};e.currentTarget.setPointerCapture(e.pointerId)}} onPointerMove={e=>{if(drag.current)onPan({x:e.clientX/side-drag.current.x,y:e.clientY/side-drag.current.y})}} onPointerUp={()=>drag.current=null} onPointerCancel={()=>drag.current=null}>
 <img draggable={false} src={src} onLoad={e=>onSize?.(e.currentTarget.naturalWidth)} alt={`${label}: SPHEREx observation acquired ${date}`} style={{width:side,height:side,imageRendering:smooth?'auto':'pixelated',transform:`translate(${pan.x*side}px,${pan.y*side}px) scale(${zoom})`}}/>
 <span className="north">N ↑ · E ←</span><span className="stamp">{label} · {date} UTC</span>
 <span className="scale" style={{width:barPixels}}><span>{(barArcmin*60).toFixed(1)}″</span></span>
 </div>
}
