import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
plt.rcParams['font.family']='DejaVu Sans'

C_BACK='#dce6f2'; E_BACK='#2e4d7b'
C_EDGE='#e8eef7'; E_EDGE='#2e4d7b'
C_VLAN='#fde9c8'; E_VLAN='#b5852a'
C_SITE='#f4f6f9'; E_SITE='#3a3a3a'
TXT='#1a1a1a'

fig,ax=plt.subplots(figsize=(9.6,5.9),dpi=300)
ax.set_xlim(0,100); ax.set_ylim(0,64); ax.axis('off')

def box(x,y,w,h,fc,ec,r=2.2,lw=1.6):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle=f'round,pad=0,rounding_size={r}',
                                fc=fc,ec=ec,lw=lw,mutation_aspect=1))

fig.canvas.draw()
_R=fig.canvas.get_renderer()
def _wpx(wunits):
    a=ax.transData.transform((0,0))[0]; b=ax.transData.transform((wunits,0))[0]
    return abs(b-a)
def fit(x,y,s,wunits,fs,w='normal',c=TXT):
    t=ax.text(x,y,s,fontsize=fs,fontweight=w,color=c,ha='center',va='center')
    bb=t.get_window_extent(renderer=_R); avail=_wpx(wunits)*0.94
    if bb.width>avail: t.set_fontsize(max(fs*avail/bb.width,10.0))
    return t
def arrow(x1,y1,x2,y2,lw=1.8,c='#2e4d7b'):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='-|>',mutation_scale=13,lw=lw,color=c))

# Top row
box(1.5,49.5,41,9.5,C_BACK,E_BACK)
fit(22,55.6,'Iraqi Telecommunications Operator',38,12.5,'bold',E_BACK)
fit(22,51.7,'Core Network / Fiber Backbone',38,11.5,'normal',E_BACK)
box(44,51,14,6,C_VLAN,E_VLAN,r=1.4)
fit(51,54.6,'Dedicated',12.5,10.5,'bold',E_VLAN)
fit(51,52.2,'Gaming VLAN',12.5,10.5,'bold',E_VLAN)
box(59.5,49,39,10,C_EDGE,E_EDGE)
fit(79,56.6,'ISP-Hosted Edge Infrastructure',36,12.5,'bold',E_EDGE)
fit(79,53.0,'Blacknut Platform Servers',36,11,'normal',TXT)
fit(79,50.5,'AMD Radeon Pro V520 GPU Servers',36,11,'normal',TXT)
arrow(42.5,54,44,54); arrow(58,54,59.5,54)

# Distribution bus
arrow(22,49.5,22,45.5,2.0)
ax.plot([17,83],[44,44],color=E_BACK,lw=2.0)
ax.plot([22,22],[45.5,44],color=E_BACK,lw=2.0)
for sx in [17,50,83]:
    ax.plot([sx,sx],[44,41],color=E_BACK,lw=2.0); arrow(sx,42,sx,38.6,1.8)

# Site boxes
def site(cx,t1,t2,sub,tags,rttline,bad=False):
    w=30; x=cx-w/2; y=7.5; h=30.5
    box(x,y,w,h,C_SITE,E_SITE,lw=1.7); iw=w-3.5
    fit(cx,y+h-3.4,t1,iw,12.5,'bold',TXT)
    fit(cx,y+h-6.4,t2,iw,11.5,'bold','#333')
    fit(cx,y+h-9.2,sub,iw,10.5,'normal','#555')
    ty=y+h-13.0
    for label,col,ec in tags:
        bw=w-4.5
        box(cx-bw/2,ty-2.9,bw,3.6,col,ec,r=1.0,lw=1.2)
        fit(cx,ty-1.1,label,bw-2.0,10.5,'bold',ec); ty-=4.7
    box(x+2,y+1.6,w-4,3.6,'#eef1f5','#888',r=1.0,lw=1.1)
    fit(cx,y+3.4,rttline,w-6,10.5,'bold','#a23b3b' if bad else '#2f5d2f')

site(17,'Onsite','(Data Center)','Optimal baseline',
     [('Wired Ethernet + Wi-Fi','#e3eee0','#4a6b46'),('PC-High  +  Mobile','#e3eef5','#2e4d7b')],
     'Avg RTT 1 ms   |   0% loss')
site(50,'Ramadi','(Remote ~100 km)','Provincial fiber link',
     [('Wi-Fi (802.11ac)','#e3eee0','#4a6b46'),('PC-High','#e3eef5','#2e4d7b')],
     'Avg RTT 10 ms   |   0% loss')
site(83,'Sina’ah Street','(Metro Baghdad)','Residential last mile',
     [('Wi-Fi (802.11ac)','#e3eee0','#4a6b46'),('PC-Low  +  Mobile','#e3eef5','#2e4d7b')],
     'RTT 8 ms | high jitter + loss',bad=True)

plt.subplots_adjust(left=0.01,right=0.99,top=0.99,bottom=0.01)
plt.savefig('results/Figure1.png',dpi=300,bbox_inches='tight',facecolor='white',pad_inches=0.06)
print('Figure1 saved')
