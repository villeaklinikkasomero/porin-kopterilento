import json, struct, numpy as np

CT = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}

class GLB:
    def __init__(s, path):
        b = open(path, "rb").read()
        L = struct.unpack("<I", b[12:16])[0]
        s.j = json.loads(b[20:20 + L])
        o = 20 + L
        bl = struct.unpack("<I", b[o:o + 4])[0]
        s.bin = b[o + 8:o + 8 + bl]

    def view(s, i):
        bv = s.j["bufferViews"][i]
        o = bv.get("byteOffset", 0)
        return s.bin[o:o + bv["byteLength"]]

    def acc(s, i):
        a = s.j["accessors"][i]
        bv = s.j["bufferViews"][a["bufferView"]]
        dt = np.dtype(CT[a["componentType"]])
        n = NC[a["type"]]
        o = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
        stride = bv.get("byteStride", 0)
        cnt = a["count"]
        if stride and stride != dt.itemsize * n:
            raw = np.frombuffer(s.bin, dtype=np.uint8, count=stride * (cnt - 1) + dt.itemsize * n, offset=o)
            out = np.empty((cnt, n), dt)
            for k in range(cnt):
                out[k] = np.frombuffer(raw[k * stride:k * stride + dt.itemsize * n].tobytes(), dt)
        else:
            out = np.frombuffer(s.bin, dtype=dt, count=cnt * n, offset=o).reshape(cnt, n)
        out = out.astype(np.float64) if dt != np.float32 or True else out
        if a.get("normalized"):
            out = out / np.iinfo(dt).max
        return out

def q2m(q):
    x, y, z, w = q
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])

def m2q(m):
    t = np.trace(m)
    if t > 0:
        s = np.sqrt(t + 1) * 2
        w = 0.25 * s; x = (m[2, 1] - m[1, 2]) / s; y = (m[0, 2] - m[2, 0]) / s; z = (m[1, 0] - m[0, 1]) / s
    elif m[0, 0] > m[1, 1] and m[0, 0] > m[2, 2]:
        s = np.sqrt(1 + m[0, 0] - m[1, 1] - m[2, 2]) * 2
        w = (m[2, 1] - m[1, 2]) / s; x = 0.25 * s; y = (m[0, 1] + m[1, 0]) / s; z = (m[0, 2] + m[2, 0]) / s
    elif m[1, 1] > m[2, 2]:
        s = np.sqrt(1 + m[1, 1] - m[0, 0] - m[2, 2]) * 2
        w = (m[0, 2] - m[2, 0]) / s; x = (m[0, 1] + m[1, 0]) / s; y = 0.25 * s; z = (m[1, 2] + m[2, 1]) / s
    else:
        s = np.sqrt(1 + m[2, 2] - m[0, 0] - m[1, 1]) * 2
        w = (m[1, 0] - m[0, 1]) / s; x = (m[0, 2] + m[2, 0]) / s; y = (m[1, 2] + m[2, 1]) / s; z = 0.25 * s
    q = np.array([x, y, z, w]); return q / np.linalg.norm(q)

def trs(n):
    if "matrix" in n:
        return np.array(n["matrix"]).reshape(4, 4).T
    M = np.eye(4)
    R = q2m(n.get("rotation", [0, 0, 0, 1]))
    S = np.diag(n.get("scale", [1, 1, 1]))
    M[:3, :3] = R @ S
    M[:3, 3] = n.get("translation", [0, 0, 0])
    return M

def rot_between(a, b):
    a = a / np.linalg.norm(a); b = b / np.linalg.norm(b)
    v = np.cross(a, b); c = np.dot(a, b)
    if np.linalg.norm(v) < 1e-9:
        return np.eye(3)
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + vx + vx @ vx * (1 / (1 + c))
