#!/usr/bin/env python3
"""Optional local ASR. Input timestamps remain in original source seconds."""
import argparse,json,subprocess
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('video',type=Path);ap.add_argument('out',type=Path);ap.add_argument('--backend',choices=['mlx','faster-whisper'],default='mlx');ap.add_argument('--model');ap.add_argument('--language',default='vi');args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=True);wav=args.out/'audio.wav'
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(args.video),'-vn','-ac','1','-ar','16000',str(wav)],check=True)
    if args.backend=='mlx':
        import mlx_whisper
        data=mlx_whisper.transcribe(str(wav),path_or_hf_repo=args.model or 'mlx-community/whisper-large-v3-turbo',language=args.language,word_timestamps=True)
        segments=data['segments']
    else:
        from faster_whisper import WhisperModel
        model=WhisperModel(args.model or 'small',device='cpu',compute_type='int8');seg,_=model.transcribe(str(wav),language=args.language,word_timestamps=True)
        segments=[{'start':s.start,'end':s.end,'text':s.text,'words':[{'word':w.word,'start':w.start,'end':w.end} for w in s.words]} for s in seg]
    words=[{'w':w['word'].strip(),'start':round(w['start'],3),'end':round(w['end'],3)} for s in segments for w in s.get('words',[])]
    (args.out/'words.json').write_text(json.dumps(words,ensure_ascii=False,indent=2));(args.out/'transcript.txt').write_text('\n'.join(f"{s['start']:.3f}-{s['end']:.3f} {s['text'].strip()}" for s in segments)+'\n')
    cuts=[]
    for w in words:
        if cuts and w['start']-cuts[-1]['end']<=.4:cuts[-1]['end']=w['end']
        else:cuts.append({'start':w['start'],'end':w['end']})
    # Suggestions only. Human/agent reviews word boundaries and meanings before editing.
    (args.out/'cuts.json').write_text(json.dumps(cuts,indent=2));print(f'{len(words)} words; {len(cuts)} suggested intervals')
if __name__=='__main__':main()
