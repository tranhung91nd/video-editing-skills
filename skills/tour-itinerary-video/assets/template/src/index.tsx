import React,{useEffect,useState} from 'react';
import {AbsoluteFill,Sequence,Img,OffthreadVideo,Audio,staticFile,useCurrentFrame,interpolate,spring,useVideoConfig,Composition,registerRoot,delayRender,continueRender} from 'remotion';
let fontPromise:Promise<void>|undefined;
function useFonts(){const [ready,setReady]=useState(false);const [handle]=useState(()=>delayRender('Bundled tour font'));useEffect(()=>{fontPromise??=new FontFace('Tour Sans',`url(${staticFile('fonts/BeVietnamPro.ttf')})`,{weight:'600'}).load().then(f=>{document.fonts.add(f);});fontPromise.then(()=>{setReady(true);continueRender(handle);}).catch(e=>{throw e;});},[handle]);return ready;}
const clamp={extrapolateLeft:'clamp',extrapolateRight:'clamp'} as const;
type Shot={s:number;e:number;src:string;day:number;title:string;sub?:string;type?:string;position?:string;focus?:string;mediaStart?:number};
const Tour:React.FC<any>=(p)=>{const ready=useFonts();const {fps}=useVideoConfig();const shots:Shot[]=p.shots;const captions=p.captions;const C=p.palette||{cream:'#faf4e8',gold:'#e6bc73',red:'#a6193d',ink:'#102c2e'};
function Brand(){
 if(!p.brand.logo)return null;
 return <div style={{position:'relative',width:260,height:260*861/1920,filter:'drop-shadow(0 2px 4px rgba(0,0,0,.35))'}}>
  <Img src={staticFile(p.brand.logo)} style={{position:'absolute',inset:0,width:'100%',height:'100%'}}/>
  <Img src={staticFile(p.brand.logo)} style={{position:'absolute',inset:0,width:'100%',height:'100%',filter:'brightness(0) invert(1)',clipPath:`inset(0 0 0 ${p.brand.whiteWordmarkFrom??40}%)`}}/>
 </div>;
}
function Media({shot,index}:{shot:Shot;index:number}){
 const f=useCurrentFrame();const frames=Math.round((shot.e-shot.s)*fps);const p=interpolate(f,[0,frames],[0,1],clamp);
 const scale=1.035+p*.065;const isVideo=shot.src.endsWith('mp4');
 return <AbsoluteFill style={{opacity:interpolate(f,[0,index===0?1:12],[0,1],clamp),overflow:'hidden'}}>
  <AbsoluteFill style={{transform:`scale(${isVideo?1.02:scale}) translateX(${(index%2===0?1:-1)*(p-.5)*18}px)`}}>
   {isVideo?<OffthreadVideo src={staticFile(shot.src)} startFrom={Math.round((shot.mediaStart??0)*fps)} muted style={{width:'100%',height:'100%',objectFit:'cover'}}/>:<Img src={staticFile(shot.src)} style={{width:'100%',height:'100%',objectFit:'cover',objectPosition:shot.focus||'50% 50%'}}/>}
  </AbsoluteFill>
  <AbsoluteFill style={{background:'linear-gradient(90deg,rgba(3,21,24,.53),transparent 68%),linear-gradient(0deg,rgba(2,18,23,.77),transparent 37%,transparent 72%,rgba(2,18,23,.35))'}}/>
 </AbsoluteFill>;
}
function Label({shot}:{shot:Shot}){
 const f=useCurrentFrame();const {fps}=useVideoConfig();const a=spring({frame:f,fps,config:{damping:22,stiffness:100}});
 if(['intro','cta'].includes(shot.type||''))return null;
 return <div style={{position:'absolute',left:106,top:shot.position==='lower'?630:164,opacity:interpolate(f,[5,20],[0,1],clamp),transform:`translateY(${(1-a)*fps}px)`,textShadow:'0 3px 20px rgba(0,0,0,.5)'}}>
  <div style={{display:'flex',alignItems:'center',gap:18,marginBottom:19}}><div style={{width:shot.day?46:64,height:3,background:C.gold}}/><span style={{color:C.gold,fontSize:25,fontWeight:600,letterSpacing:4}}>{shot.day?`NGÀY 0${shot.day}`:p.region}</span></div>
  <div style={{fontSize:shot.title.length>25?58:72,fontWeight:700,letterSpacing:-1.5,color:C.cream,lineHeight:1.15}}>{shot.title}</div>
  {shot.sub&&<div style={{marginTop:21,fontSize:29,fontWeight:500,color:'#f6f1e8'}}>{shot.sub}</div>}
 </div>;
}
const routePoints=p.routePoints;
function Route({compact=false}:{compact?:boolean}){
 const f=useCurrentFrame();let routeProgress=interpolate(f,[8,110],[0,1],clamp);
 if(compact)return <TrainRoute/>;
 const path='M120 405 Q230 220 460 250 Q640 60 830 110 Q1090 150 1140 380';
 return <div style={{position:'absolute',left:compact?370:210,top:compact?400:470,width:compact?1200:1500,height:compact?420:450,opacity:interpolate(f,[0,16],[0,1],clamp)}}>
  <svg viewBox="0 0 1280 500" width="100%" height="100%">
   <path d={path} fill="none" stroke={C.cream} opacity=".25" strokeWidth="3" strokeDasharray="7 11"/>
   <path d={path} pathLength="1" fill="none" stroke={C.gold} strokeWidth="5" strokeDasharray="1" strokeDashoffset={1-routeProgress}/>
   {routePoints.map((point,i)=> <g key={point.name} opacity={interpolate(f,[i*20,i*20+12],[0,1],clamp)}><circle cx={point.x} cy={point.y} r="14" fill={C.gold}/><circle cx={point.x} cy={point.y} r="24" stroke={C.gold} fill="none" opacity=".4"/><text x={point.x} y={point.y+62} textAnchor="middle" fill={C.cream} fontFamily={p.fontFamily||"Tour Sans"} fontSize="25" fontWeight="600">{point.name}</text></g>)}
  </svg>
 </div>;
}
function TrainRoute(){
 const f=useCurrentFrame();const railProgress=interpolate(f,[10,74],[0,1],clamp);const x=220+railProgress*840;
 return <div style={{position:'absolute',left:210,top:410,width:1500,height:420,opacity:interpolate(f,[0,10],[0,1],clamp)}}>
  <svg viewBox="0 0 1280 360" width="100%" height="100%">
   <path d="M220 180 H1060" stroke={C.cream} strokeWidth="3" opacity=".25"/>
   <path d="M220 180 H1060" stroke={C.gold} strokeWidth="5" pathLength="1" strokeDasharray="1" strokeDashoffset={1-railProgress}/>
   {[220,1060].map((cx,i)=><g key={cx}><circle cx={cx} cy="180" r="15" fill={C.gold}/><circle cx={cx} cy="180" r="27" fill="none" stroke={C.gold} opacity=".4"/><text x={cx} y="255" textAnchor="middle" fill={C.cream} fontSize="35" fontFamily={p.fontFamily||"Tour Sans"} fontWeight="700">{i?p.rail.to:p.rail.from}</text></g>)}
   <g transform={`translate(${x-50} 96)`}><path d="M4 40 H-20 M0 55 H-30" stroke={C.gold} strokeWidth="4"/><path d="M12 15 H68 Q92 15 108 58 L112 65 H12 Z" fill={C.cream}/><path d="M20 27 H49 V43 H20 Z M58 27 H76 L89 43 H58 Z" fill={C.ink}/><path d="M13 53 H103" stroke={C.red} strokeWidth="6"/><circle cx="29" cy="69" r="7" fill={C.gold}/><circle cx="84" cy="69" r="7" fill={C.gold}/></g>
   <text x="640" y="320" textAnchor="middle" fill={C.gold} fontSize="22" letterSpacing="5" fontFamily={p.fontFamily||"Tour Sans"}>{p.rail.label}</text>
  </svg>
 </div>;
}
function Intro(){
 const f=useCurrentFrame();
 return <AbsoluteFill style={{background:'rgba(3,30,33,.65)'}}>
  <div style={{position:'absolute',left:106,top:165,color:C.gold,fontSize:27,letterSpacing:6}}>{p.intro.kicker}</div>
  <div style={{position:'absolute',left:100,top:210,fontSize:108,fontWeight:700,letterSpacing:-4,transform:`translateY(${interpolate(f,[0,22],[45,0],clamp)}px)`,opacity:interpolate(f,[0,15],[0,1],clamp)}}>{p.intro.title} <span style={{color:C.gold}}>{p.intro.accent}</span></div>
  <div style={{position:'absolute',left:110,top:355,fontSize:31,letterSpacing:2}}>{p.intro.routeLabel}</div>
  <Route/>
  <div style={{position:'absolute',right:105,top:174,display:'flex',gap:22}}>{p.intro.photos.map((x,i)=><div key={x} style={{width:220,height:268,overflow:'hidden',border:'7px solid #faf4e8',boxShadow:'0 14px 35px #0005',transform:`rotate(${i?6:-5}deg) translateY(${interpolate(f,[15+i*8,45+i*8],[65,0],clamp)}px)`,opacity:interpolate(f,[15+i*8,30+i*8],[0,1],clamp)}}><Img src={staticFile(x)} style={{width:'100%',height:'100%',objectFit:'cover'}}/></div>)}</div>
 </AbsoluteFill>;
}
function Postcard(){
 const f=useCurrentFrame();
 return <AbsoluteFill style={{background:C.ink}}>
  <div style={{position:'absolute',left:100,top:400,width:850,height:435,overflow:'hidden',border:'9px solid #faf4e8',transform:`rotate(-2deg) translateY(${interpolate(f,[0,20],[40,0],clamp)}px)`}}><Img src={staticFile(p.postcards?.[0]||p.intro.photos[0])} style={{width:'100%',height:'100%',objectFit:'cover'}}/></div>
  <div style={{position:'absolute',left:1000,top:440,width:820,height:360,overflow:'hidden',border:'9px solid #faf4e8',transform:'rotate(3deg)'}}><Img src={staticFile(p.postcards?.[1]||p.intro.photos[1])} style={{width:'100%',height:'100%',objectFit:'cover'}}/></div>
 </AbsoluteFill>;
}
function CTA(){
 const f=useCurrentFrame();const {fps}=useVideoConfig();let a=spring({frame:f,fps,config:{damping:24}});
 return <AbsoluteFill style={{background:'linear-gradient(90deg,rgba(8,35,38,.97) 0%,rgba(8,35,38,.94) 52%,rgba(8,35,38,.38) 100%)'}}>
  <div style={{position:'absolute',left:106,top:170,width:1070,transform:`translateY(${(1-a)*35}px)`,opacity:a}}>
   <div style={{fontSize:27,color:C.gold,letterSpacing:4,marginBottom:29}}>{p.cta.kicker}</div>
   <div style={{fontSize:87,fontWeight:700,lineHeight:1.13,letterSpacing:-3}}>{p.cta.title}<br/><span style={{color:C.gold}}>{p.cta.accent}</span></div>
   <div style={{display:'flex',gap:17,marginTop:43}}>{p.cta.chips.map((s,i)=><div key={s} style={{border:'1px solid #e6bc7370',borderRadius:30,padding:'13px 24px',fontSize:25,opacity:interpolate(f,[20+i*9,35+i*9],[0,1],clamp)}}>{s}</div>)}</div>
   <div style={{marginTop:41,fontSize:31,lineHeight:1.5}}>{p.cta.prompt}</div>
   <div style={{marginTop:34,display:'inline-flex',alignItems:'center',gap:32,background:C.red,padding:'20px 34px',borderRadius:8,fontSize:30,fontWeight:700}}>{p.cta.button} <span style={{fontSize:36}}>→</span></div>
  </div>
  <div style={{position:'absolute',right:86,top:250,width:475,height:460,borderRadius:240,overflow:'hidden',border:'3px solid #e6bc73aa',boxShadow:'0 0 0 16px #ffffff07',transform:`translateY(${Math.sin(f/80)*7}px)`}}><Img src={staticFile(p.cta.image)} style={{height:'100%',width:'100%',objectFit:'cover'}}/></div>
 </AbsoluteFill>;
}
function Progress(){
 const f=useCurrentFrame();const day=shots.find(s=>f/fps>=s.s&&f/fps<s.e)?.day||0;
 if(!day)return null;
 return <div style={{position:'absolute',bottom:41,left:108,right:108,display:'flex',gap:15}}>{p.days.map(d=><div key={d} style={{flex:1,display:'flex',alignItems:'center',gap:10,opacity:d<=day?1:.45}}><div style={{height:3,background:d<=day?C.gold:'#ffffff60',flex:1}}/><span style={{fontSize:17,letterSpacing:2,color:d===day?C.gold:C.cream}}>NGÀY 0{d}</span></div>)}</div>;
}
function Journey(){
 const f=useCurrentFrame();const {durationInFrames,fps}=useVideoConfig();const caption=captions.find(c=>f/fps*1000>=c.startMs&&f/fps*1000<c.endMs);
 return <AbsoluteFill style={{background:C.ink,color:C.cream,fontFamily:p.fontFamily||'Tour Sans, sans-serif'}}>
  {shots.map((s,i)=><Sequence key={i} from={Math.round(s.s*fps)} durationInFrames={Math.min(durationInFrames-Math.round(s.s*fps),Math.round((s.e-s.s)*fps)+12)}><Media shot={s} index={i}/></Sequence>)}
  {shots.map((s,i)=><Sequence key={`label-${i}`} from={Math.round(s.s*fps)} durationInFrames={Math.round((s.e-s.s)*fps)}>{s.type==='postcard'&&<Postcard/>}{s.type==='route'&&<AbsoluteFill style={{background:'rgba(5,35,38,.52)'}}/>}<Label shot={s}/>{s.type==='intro'&&<Intro/>}{s.type==='route'&&<Route compact/>}{s.type==='cta'&&<CTA/>}</Sequence>)}
  <div style={{position:'absolute',left:106,top:25}}><Brand/></div>
  <div style={{position:'absolute',top:61,right:108,fontSize:18,letterSpacing:4,color:'#fff9'}}>{p.edition}</div>
  <Progress/>
  {caption&&<div style={{position:'absolute',left:100,right:100,bottom:94,display:'flex',justifyContent:'center'}}><div style={{fontSize:36,fontWeight:500,lineHeight:1.3,textAlign:'center',padding:'11px 24px',background:'rgba(4,20,24,.76)',borderRadius:8,textShadow:'0 2px 4px #0008',maxWidth:1640}}>{caption.text}</div></div>}
  <div style={{position:'absolute',bottom:0,left:0,height:4,width:`${f/durationInFrames*100}%`,background:C.gold}}/>
  <AbsoluteFill style={{background:C.ink,opacity:interpolate(f,[durationInFrames-Math.round(1.2*fps),durationInFrames-1],[0,1],clamp),pointerEvents:'none'}}/>
  <Audio src={staticFile(p.voice.file)}/>
  {p.music?.file&&<Audio src={staticFile(p.music.file)} volume={(f)=>{const start=p.duration-(p.music.fadeOut??4);return (p.music.volume??.32)*interpolate(f/fps,[0,p.music.fadeIn??.4,start,p.duration],[0,1,1,0],clamp);}}/>}
 </AbsoluteFill>;
}

return ready?<Journey/>:null;
};
registerRoot(()=> <Composition id="Tour" component={Tour} width={1920} height={1080} fps={30} durationInFrames={30} defaultProps={{duration:1,fps:30}} calculateMetadata={({props}:any)=>({fps:props.fps??30,durationInFrames:Math.round(props.duration*(props.fps??30))})}/>);
