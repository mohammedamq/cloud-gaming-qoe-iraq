import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
plt.rcParams['font.family']='DejaVu Sans'
TXT='#1a1a1a'
fig,ax=plt.subplots(figsize=(9.6,6.7),dpi=300)
ax.set_xlim(0,100); ax.set_ylim(0,74); ax.axis('off')

def box(x,y,w,h,fc,ec,r=1.4,lw=1.6):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle=f'round,pad=0,rounding_size={r}',fc=fc,ec=ec,lw=lw,mutation_aspect=1))
fig.canvas.draw(); _R=fig.canvas.get_renderer()
def _wpx(wu):
    a=ax.transData.transform((0,0))[0]; b=ax.transData.transform((wu,0))[0]; return abs(b-a)
def fit(x,y,s,wu,fs,w='normal',c=TXT,ha='center'):
    t=ax.text(x,y,s,fontsize=fs,fontweight=w,color=c,ha=ha,va='center')
    bb=t.get_window_extent(renderer=_R); avail=_wpx(wu)*0.94
    if bb.width>avail: t.set_fontsize(max(fs*avail/bb.width,10.0))
    return t
def arrow(x1,y1,x2,y2,lw=2.0,c='#3a3a3a'):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='-|>',mutation_scale=15,lw=lw,color=c))

E1='#2e4d7b'; F1='#dce6f2'; E2='#4a6b46'; F2='#e3eee0'; E3='#7a5a2a'; F3='#fbecd2'

# Stage 1
box(8,65,84,6.6,F1,E1,lw=1.8)
fit(50,68.3,'Stage 1: Test Scenario Configuration (16 unique scenarios)',80,13,'bold',E1)
chips=[('Location',['3 sites'],13.5),('Connection',['Wired, Wi-Fi'],37),
       ('Device',['PC-High, PC-Low,','Mobile'],61),('Game',['Heavy, Moderate,','Light'],85)]
for title,levels,cx in chips:
    cw=21; box(cx-cw/2,55.5,cw,7.6,'#eef3fa',E1,lw=1.3)
    fit(cx,61.4,title,cw-2.5,10.8,'bold',E1)
    yy=59.2 if len(levels)==1 else 59.4
    for ln in levels:
        fit(cx,yy,ln,cw-2.5,10.2,'normal',E1); yy-=2.3
arrow(50,55.3,50,51.8,2.2,c=E1)

# Stage 2
box(8,22,84,29,F2,E2,lw=1.8)
fit(50,48.3,'Stage 2: Active Session and Concurrent Data Collection',80,13,'bold',E2)
rows=[('Game streaming','Blacknut WebRTC, 720p / 30 fps, 8 Mbps'),
      ('Network latency','ICMP ping, 1 s granularity, RTT and loss'),
      ('Traffic volume','PRTG Monitor, 10-20 s, bandwidth profile'),
      ('Packet capture','Wireshark: jitter SD, retransmission, out-of-order'),
      ('Input lag','120 fps camera + controller LED (button-to-photon)')]
ry=44.0
for kx,vx in rows:
    box(11,ry-3.2,24,3.9,'#f4f8f3',E2,lw=1.2); fit(23,ry-1.25,kx,22,10.6,'bold',E2)
    box(36,ry-3.2,53,3.9,'#ffffff','#9bb597',lw=1.0); fit(62.5,ry-1.25,vx,51,10.4,'normal',TXT)
    ry-=4.45
arrow(50,21.7,50,18.2,2.2,c=E2)

# Stage 3
box(8,5,84,11,F3,E3,lw=1.8)
fit(50,13.4,'Stage 3: Integrated Analysis and QoE Assessment',80,13,'bold',E3)
outs=[('Per-scenario','distributions',19),('Correlation and','descriptive fit',41.5),
      ('netem controlled','replay',62),('Inter-rater','agreement (kappa)',83)]
for l1,l2,cx in outs:
    cw=20; box(cx-cw/2,6.3,cw,4.8,'#fdf4e3',E3,lw=1.2)
    fit(cx,9.3,l1,cw-2,10.2,'bold',E3); fit(cx,7.4,l2,cw-2,10.2,'bold',E3)

plt.subplots_adjust(left=0.01,right=0.99,top=0.99,bottom=0.01)
plt.savefig('results/Figure2.png',dpi=300,bbox_inches='tight',facecolor='white',pad_inches=0.06)
print('Figure2 saved')
