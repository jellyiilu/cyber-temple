"""Build a self-contained stylized golden seated Buddha GLB from parametric meshes."""
import json, math, struct
from pathlib import Path

OUT = Path(__file__).with_name('buddha-golden.glb')
materials = [
    {"name":"Warm gilded bronze", "pbrMetallicRoughness":{"baseColorFactor":[0.83,0.58,0.19,1],"metallicFactor":0.72,"roughnessFactor":0.32}},
    {"name":"Recessed patina", "pbrMetallicRoughness":{"baseColorFactor":[0.28,0.16,0.055,1],"metallicFactor":0.48,"roughnessFactor":0.58}},
    {"name":"Bodhi bark", "pbrMetallicRoughness":{"baseColorFactor":[0.20,0.12,0.065,1],"metallicFactor":0.05,"roughnessFactor":0.92}},
    {"name":"Bodhi leaves", "pbrMetallicRoughness":{"baseColorFactor":[0.26,0.36,0.16,1],"metallicFactor":0.04,"roughnessFactor":0.8}},
]
meshes=[]

def add_mesh(pos, faces, mat=0, name='part'):
    # Ensure outward normals on the common closed, centered primitive meshes.
    normals=[[0.,0.,0.] for _ in pos]
    for face in faces:
        a,b,c=(pos[i] for i in face)
        u=[b[k]-a[k] for k in range(3)]; v=[c[k]-a[k] for k in range(3)]
        n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
        for i in face:
            for k in range(3): normals[i][k]+=n[k]
    for i,n in enumerate(normals):
        l=math.sqrt(sum(x*x for x in n)) or 1
        normals[i]=[x/l for x in n]
    meshes.append((name,mat,pos,normals,faces))

def uv_sphere(center, scale, mat=0, name='golden form', seg=28, rings=18):
    x0,y0,z0=center; sx,sy,sz=scale; pos=[]
    for j in range(rings+1):
        th=math.pi*j/rings
        for i in range(seg):
            ph=2*math.pi*i/seg
            pos.append([x0+sx*math.sin(th)*math.cos(ph),y0+sy*math.cos(th),z0+sz*math.sin(th)*math.sin(ph)])
    faces=[]
    for j in range(rings):
        for i in range(seg):
            a=j*seg+i; b=j*seg+(i+1)%seg; c=(j+1)*seg+(i+1)%seg; d=(j+1)*seg+i
            faces.extend([[a,b,d],[b,c,d]])
    add_mesh(pos,faces,mat,name)

def catmull(points, steps=8):
    out=[]
    for i in range(len(points)-1):
        p0=points[max(0,i-1)]; p1=points[i]; p2=points[i+1]; p3=points[min(len(points)-1,i+2)]
        for j in range(steps):
            t=j/steps; t2=t*t; t3=t2*t
            out.append([.5*((2*p1[k])+(-p0[k]+p2[k])*t+(2*p0[k]-5*p1[k]+4*p2[k]-p3[k])*t2+(-p0[k]+3*p1[k]-3*p2[k]+p3[k])*t3) for k in range(3)])
    out.append(points[-1]); return out

def tube(points, radius, mat=0, name='robe fold', sides=10):
    path=catmull(points,6); pos=[]; faces=[]
    for i,p in enumerate(path):
        prev=path[max(i-1,0)]; nxt=path[min(i+1,len(path)-1)]
        tangent=[nxt[k]-prev[k] for k in range(3)]; ll=math.sqrt(sum(x*x for x in tangent)) or 1; tangent=[x/ll for x in tangent]
        ref=[0,1,0] if abs(tangent[1])<.9 else [1,0,0]
        u=[tangent[1]*ref[2]-tangent[2]*ref[1],tangent[2]*ref[0]-tangent[0]*ref[2],tangent[0]*ref[1]-tangent[1]*ref[0]]
        ul=math.sqrt(sum(x*x for x in u)) or 1; u=[x/ul for x in u]
        v=[tangent[1]*u[2]-tangent[2]*u[1],tangent[2]*u[0]-tangent[0]*u[2],tangent[0]*u[1]-tangent[1]*u[0]]
        for j in range(sides):
            a=2*math.pi*j/sides
            pos.append([p[k]+radius*(math.cos(a)*u[k]+math.sin(a)*v[k]) for k in range(3)])
    for i in range(len(path)-1):
        for j in range(sides):
            a=i*sides+j; b=i*sides+(j+1)%sides; c=(i+1)*sides+(j+1)%sides; d=(i+1)*sides+j
            faces.extend([[a,b,d],[b,c,d]])
    add_mesh(pos,faces,mat,name)

def lathe(profile, mat=0, name='robe and torso', seg=64):
    pos=[]
    for r,y in profile:
        for i in range(seg):
            a=2*math.pi*i/seg; pos.append([r*math.cos(a),y,.78*r*math.sin(a)])
    faces=[]
    for j in range(len(profile)-1):
        for i in range(seg):
            a=j*seg+i;b=j*seg+(i+1)%seg;c=(j+1)*seg+(i+1)%seg;d=(j+1)*seg+i
            faces.extend([[a,d,b],[b,d,c]])
    add_mesh(pos,faces,mat,name)

def cylinder_between(a,b,r,mat,name='branch',sides=10):
    d=[b[i]-a[i] for i in range(3)]; l=math.sqrt(sum(x*x for x in d))
    if l<1e-6:return
    axis=[x/l for x in d]; ref=[0,1,0] if abs(axis[1])<.9 else [1,0,0]
    u=[axis[1]*ref[2]-axis[2]*ref[1],axis[2]*ref[0]-axis[0]*ref[2],axis[0]*ref[1]-axis[1]*ref[0]]; ul=math.sqrt(sum(x*x for x in u));u=[x/ul for x in u]
    v=[axis[1]*u[2]-axis[2]*u[1],axis[2]*u[0]-axis[0]*u[2],axis[0]*u[1]-axis[1]*u[0]]
    pos=[]
    for p in [a,b]:
        for j in range(sides):
            t=2*math.pi*j/sides;pos.append([p[k]+r*(math.cos(t)*u[k]+math.sin(t)*v[k]) for k in range(3)])
    faces=[]
    for j in range(sides): faces.extend([[j,(j+1)%sides,sides+j],[(j+1)%sides,sides+(j+1)%sides,sides+j]])
    add_mesh(pos,faces,mat,name)

# Cross-legged silhouette, layered lap cloth and folds.
uv_sphere((0,.52,.02),(1.17,.32,.72),name='cross-legged lower robe')
uv_sphere((-.90,.45,.10),(.69,.34,.66),name='left knee')
uv_sphere((.90,.45,.10),(.69,.34,.66),name='right knee')
uv_sphere((0,.72,.40),(.91,.21,.48),name='folded legs')
for k in range(6):
    y=.38+k*.085
    tube([[-1.25+k*.055,y+.12,.32],[-.82,y-.015,.61],[-.35,y-.07,.81],[0,y-.07,.85],[.45,y-.015,.78],[.96-k*.055,y+.10,.40]],.018,1 if k%2 else 0,'incised lap pleat')

# Torso robe, chest, neck folds and head.
lathe([[0,.78],[.52,.82],[.67,1.0],[.61,1.26],[.58,1.58],[.64,1.9],[.79,2.18],[.86,2.36],[.76,2.49],[.48,2.58],[.24,2.62],[0,2.62]])
uv_sphere((0,2.27,0),(.81,.42,.54),name='shoulders')
for y in [2.61,2.69,2.77]:
    # front neck bands
    tube([[-.21,y,.18],[-.15,y-.025,.25],[0,y-.035,.27],[.15,y-.025,.25],[.21,y,.18]],.012,1,'neck crease')
uv_sphere((0,3.23,.015),(.47,.53,.405),name='serene face',seg=40,rings=28)
uv_sphere((0,2.94,.095),(.30,.20,.32),name='chin')
for s in [-1,1]:
    uv_sphere((s*.465,3.22,-.015),(.085,.29,.12),name='elongated ear')
    uv_sphere((s*.478,3.16,.068),(.042,.10,.052),1,'ear inset')
    tube([[s*.31,3.38,.345],[s*.24,3.35,.39],[s*.15,3.345,.407],[s*.07,3.37,.40]],.014,1,'closed eyelid')
    tube([[s*.31,3.47,.33],[s*.22,3.50,.365],[s*.12,3.49,.386],[s*.055,3.46,.39]],.012,0,'brow')
    tube([[s*.07,3.13,.396],[s*.14,3.105,.4],[s*.22,3.115,.376]],.011,1,'cheek contour')
uv_sphere((0,3.31,.406),(.05,.12,.06),name='nose bridge')
uv_sphere((0,3.23,.445),(.08,.05,.06),name='nose tip')
tube([[-.105,3.075,.394],[-.055,3.055,.424],[0,3.052,.43],[.055,3.055,.424],[.105,3.075,.394]],.014,1,'soft smile')
uv_sphere((0,3.025,.39),(.08,.022,.032),name='lower lip')
uv_sphere((0,3.55,.397),(.033,.033,.025),1,'urna')

# Pointed ushnisha and tightly spaced curls.
uv_sphere((0,3.67,-.005),(.37,.24,.34),name='curled hair cap')
uv_sphere((0,3.87,-.025),(.16,.20,.16),name='ushnisha')
for row in range(7):
    elev=.12+row*.19; count=max(9,round(22*math.cos(elev)))
    for i in range(count):
        a=i/count*2*math.pi+(row%2)*math.pi/count
        x=.372*math.cos(elev)*math.sin(a); y=3.67+.242*math.sin(elev); z=-.005+.342*math.cos(elev)*math.cos(a)
        if y>3.52: uv_sphere((x,y,z),(.031,.031,.027),name='snail-shell curl',seg=10,rings=8)
uv_sphere((0,4.07,-.025),(.065,.11,.065),name='finial')

# Hands and sleeves: raised right palm on the viewer's left, fingers upright.
tube([[-.62,2.34,0],[-.78,2.13,.12],[-.88,1.93,.27],[-.91,2.12,.39]],.15,0,'raised sleeve')
uv_sphere((-.91,2.25,.43),(.20,.28,.115),name='raised palm')
for i in range(4):
    x=-1.035+i*.083; base=2.39+math.sin(i/3*math.pi)*.035; tip=2.77-abs(1.5-i)*.045
    tube([[x,base,.47],[x-.008,base+.12,.49],[x-.006,tip-.08,.49],[x,tip,.475]],.032,0,'upright finger')
    uv_sphere((x,tip,.475),(.032,.04,.034),name='finger tip',seg=12,rings=8)
tube([[-.75,2.31,.45],[-.69,2.4,.49],[-.69,2.51,.48],[-.74,2.55,.46]],.034,0,'thumb')
# Resting arm and draped fingers.
tube([[.61,2.34,0],[.82,2.11,.12],[.83,1.78,.32],[.56,1.34,.52],[.25,.94,.62]],.14,0,'resting sleeve')
uv_sphere((.17,.90,.68),(.23,.12,.16),name='resting hand')
for i in range(4):
    x=.04+i*.085
    tube([[x,.91,.77],[x-.005,.79,.79],[x+.012,.66,.76]],.024,0,'resting finger')
tube([[.03,.9,.77],[-.08,.82,.78],[-.12,.73,.75]],.026,0,'resting thumb')

# Sash over shoulder and flowing robe folds across chest.
for i in range(4):
    d=i*.085
    tube([[.69-d,2.42,.42],[.49-d,2.22,.55],[.22-d,1.98,.61],[-.08-d,1.72,.62],[-.42-d,1.48,.53]],.024,1 if i%2 else 0,'diagonal robe fold')
tube([[-.66,2.36,.31],[-.79,2.02,.4],[-.71,1.64,.48],[-.48,1.35,.55]],.03,0,'robe edge')
for i in range(5):
    x=-.42+i*.16
    tube([[x,1.53,.56],[x+.1,1.31,.67],[x+.15,1.12,.71],[x+.2,1.0,.66]],.018,1 if i%2 else 0,'robe pleat')

# A restrained, branching Bodhi canopy behind the statue, echoing the reference.
for side in [-1,1]:
    tube([[side*.10,.10,-.64],[side*.12,1.2,-.70],[side*.18,2.7,-.72],[side*.34,4.2,-.78],[side*.50,5.25,-.85]],.13,2,'Bodhi trunk',12)
    for j in range(4):
        start_y=2.9+j*.32; x=side*(.18+j*.08)
        tube([[x,start_y,-.73],[side*.55,start_y+.45,-.82],[side*(1.25+j*.14),start_y+.72,-.88],[side*(1.8+j*.18),start_y+1.05,-.94]],.045-j*.005,2,'Bodhi branch',8)
        for k in range(4):
            lx=side*(.85+k*.45); ly=start_y+.6+(k%2)*.32; lz=-.91
            uv_sphere((lx,ly,lz),(.32,.12,.20),3,'Bodhi leaf',seg=12,rings=8)

# Small unifying base.
for y,r,h in [(0.06,1.50,.12),(0.14,1.42,.07)]:
    # rings as lathed shallow beveled tiers
    lathe([[r*.90,y],[r,y+.025],[r,y+h-.025],[r*.92,y+h],[0,y+h]],0,'lotus base',48)

# Pack separate named meshes into one GLB, preserving material assignments.
binary=bytearray(); accessors=[]; views=[]; gltf_meshes=[]; nodes=[]
def align4():
    while len(binary)%4: binary.append(0)
def blob(data,target=None):
    align4(); off=len(binary); binary.extend(data); ix=len(views); v={"buffer":0,"byteOffset":off,"byteLength":len(data)}
    if target:v["target"]=target
    views.append(v); return ix
for name,mat,pos,normals,faces in meshes:
    flatp=[v for row in pos for v in row]; flatn=[v for row in normals for v in row]; flati=[i for f in faces for i in f]
    pi=blob(struct.pack('<%sf'%len(flatp),*flatp),34962)
    ni=blob(struct.pack('<%sf'%len(flatn),*flatn),34962)
    ii=blob(struct.pack('<%sI'%len(flati),*flati),34963)
    pmin=[min(p[k] for p in pos) for k in range(3)]; pmax=[max(p[k] for p in pos) for k in range(3)]
    ap=len(accessors);accessors.append({"bufferView":pi,"componentType":5126,"count":len(pos),"type":"VEC3","min":pmin,"max":pmax})
    an=len(accessors);accessors.append({"bufferView":ni,"componentType":5126,"count":len(normals),"type":"VEC3"})
    ai=len(accessors);accessors.append({"bufferView":ii,"componentType":5125,"count":len(flati),"type":"SCALAR"})
    gltf_meshes.append({"name":name,"primitives":[{"attributes":{"POSITION":ap,"NORMAL":an},"indices":ai,"material":mat}]})
    nodes.append({"name":name,"mesh":len(gltf_meshes)-1})
align4()
doc={"asset":{"version":"2.0","generator":"Parametric Buddha model builder"},"scene":0,"scenes":[{"nodes":list(range(len(nodes)))}],"nodes":nodes,"meshes":gltf_meshes,"materials":materials,"buffers":[{"byteLength":len(binary)}],"bufferViews":views,"accessors":accessors}
j=json.dumps(doc,separators=(',',':')).encode('utf8'); j+=b' '*((4-len(j)%4)%4)
total=12+8+len(j)+8+len(binary)
OUT.write_bytes(struct.pack('<4sII',b'glTF',2,total)+struct.pack('<I4s',len(j),b'JSON')+j+struct.pack('<I4s',len(binary),b'BIN\x00')+binary)
print(f'Wrote {OUT} ({OUT.stat().st_size:,} bytes, {len(meshes)} meshes, {sum(len(x[4]) for x in meshes):,} triangles)')
