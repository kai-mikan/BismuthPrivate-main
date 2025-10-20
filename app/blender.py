import bpy
import bmesh
from PIL import Image, ImageFile
import os, sys
import math 
from contextlib import contextmanager


@contextmanager
def stdout_redirected(to=os.devnull):
    """
    import os

    with stdout_redirected(to=filename):
        print("from Python")
        os.system("echo non-Python applications are also supported")
    """
    fd = sys.stdout.fileno()

    ##### assert that Python and C stdio write using the same file descriptor
    ####assert libc.fileno(ctypes.c_void_p.in_dll(libc, "stdout")) == fd == 1

    def _redirect_stdout(to):
        sys.stdout.close()  # + implicit flush()
        os.dup2(to.fileno(), fd)  # fd writes to 'to' file
        sys.stdout = os.fdopen(fd, "w")  # Python writes to fd

    with os.fdopen(os.dup(fd), "w") as old_stdout:
        with open(to, "w") as file:
            _redirect_stdout(to=file)
        try:
            yield  # allow code to be run with the redirected stdout
        finally:
            _redirect_stdout(to=old_stdout)  # restore stdout.
            # buffering and flags such as
            # CLOEXEC may be different

class Blender: 
#基本操作

    #初期化、シーンを開く
    def __init__(self, scenePath="/app/blank.blend"):
        self.scenePath = scenePath
        self.open_scene(scenePath)

    #モード切り替え
    def set_mode(self, mode):
        bpy.ops.object.mode_set(mode=mode)

    #.blendファイルを開く
    def open_scene(self, scenePath):
        bpy.ops.wm.open_mainfile(filepath=scenePath)
        self.context = bpy.context
        self.scene = self.context.scene
        self.camera = self.scene.camera

    #.blendファイルを保存
    def save_scene(self, scenePath="/app/result.blend"):
        bpy.ops.wm.save_as_mainfile(filepath=scenePath)

    #レンダリング実行
    def render(self, outputPath="output.png") -> ImageFile:
        pastLocation = tuple([a for a in self.camera.location])
        self.scene.render.filepath = outputPath

        with stdout_redirected():
            bpy.ops.render.render(write_still=True)
        self.camera.location = pastLocation
        return Image.open(outputPath)
    
#=============================================================================================   
#オブジェクト情報取得

    #全オブジェクト取得
    def all_objects(self) -> list:
        return list(bpy.data.objects)

    #名前でオブジェクト取得
    def get_object(self, name: str) -> list:
        return bpy.data.objects[name]

    #オブジェクト位置取得
    def locate_object(self, object_name: str) -> tuple[float, float, float]:
        obj = self.get_object(object_name)
        return (obj.location.x, obj.location.y, obj.location.z)

#=============================================================================================   
#オブジェクト操作

    #立方体を追加
    def add_cube(self, x, y, z) -> str:
        past = self.all_objects()
        bpy.ops.mesh.primitive_cube_add(location=(x, y, z))
        for object in self.all_objects():
            if object not in past:
                return object.name

    #スザンヌを追加
    def add_suzanne(self, x, y, z) -> str:
        past = self.all_objects()
        bpy.ops.mesh.primitive_monkey_add(location=(x, y, z))
        for object in self.all_objects():
            if object not in past:
                return object.name

    #オブジェクトの絶対移動 
    def relative_move_object(self, object_name: str, x: float, y: float, z: float):
        obj = self.get_object(object_name) 

        obj.location.x += x
        obj.location.y += y
        obj.location.z += z

    #オブジェクトの相対移動
    def absolute_move_object(self, object_name: str, dx: float, dy: float, dz: float):
        obj = self.get_object(object_name) 

        obj.location.x = dx
        obj.location.y = dy
        obj.location.z = dz

    #オブジェクトのスケール変更
    def scale_object(self, object_name: str, scale_x: float, scale_y: float, scale_z: float):
        obj = self.get_object(object_name)
        obj.scale.x = scale_x
        obj.scale.y = scale_y
        obj.scale.z = scale_z

    #オブジェクトの均一スケール変更
    def scale_object_uniform(self, object_name: str, scale: float):
        self.scale_object(object_name, scale, scale, scale)
    
    #ブーリアン演算でオブジェクト統合
    def boolean_union(self, base_name: str, target_name: str) -> str:
        base_obj = self.get_object(base_name)
        target_obj = self.get_object(target_name)
        
        # ブーリアンモディファイアを追加
        modifier = base_obj.modifiers.new(name="Boolean", type='BOOLEAN')
        modifier.operation = 'UNION'
        modifier.object = target_obj
        
        # モディファイアを適用
        bpy.context.view_layer.objects.active = base_obj
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        
        # ターゲットオブジェクトを削除
        bpy.data.objects.remove(target_obj, do_unlink=True)
        
        return base_obj.name    

    #複数のオブジェクトをブーリアン統合
    def boolean_union_multiple(self, base_name: str, object_names: list[str]) -> str:
        result_name = base_name
        
        for target_name in object_names:
            result_name = self.boolean_union(result_name, target_name)
        
        return result_name

#=============================================================================================   
#メッシュ情報取得

    #頂点数を取得
    def count_vertex(self, object_name: str) -> int:
        vertices = self.get_object(object_name).data.vertices
        return len(vertices)

    #頂点座標取得
    def locate_vertex(self, object_name: str, vertex_index: int) -> tuple[float, float, float]:
        mesh = self.get_object(object_name).data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.verts.ensure_lookup_table()
        x, y, z = bm.verts[vertex_index].co
        bm.free()
        return x, y, z
    
    #頂点を共有する面のインデックスリストを取得
    def get_vertex_faces(self, object_name: str, vertex_index: int) -> list[int]:
        mesh = self.get_object(object_name).data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.verts.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        
        vertex = bm.verts[vertex_index]
        face_indices = [face.index for face in vertex.link_faces]
        
        bm.free()
        return face_indices
    
    #指定頂点において隣り合う面のペアを取得
    def get_adjacent_face_pairs(self, object_name: str, vertex_index: int) -> list[tuple[int, int]]:
        mesh = self.get_object(object_name).data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.verts.ensure_lookup_table()
        
        vertex = bm.verts[vertex_index]
        
        # 頂点を共有するエッジを取得
        edges = vertex.link_edges
        
        adjacent_pairs = []
        for edge in edges:
            # エッジを共有する面（最大2つ）を取得
            faces = edge.link_faces
            if len(faces) == 2:
                adjacent_pairs.append((faces[0].index, faces[1].index))
        
        bm.free()
        return adjacent_pairs

    #面の法線ベクトルを取得
    def get_face_normal(self, object_name: str, face_index: int) -> tuple[float, float, float]:
        mesh = self.get_object(object_name).data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.faces.ensure_lookup_table()
        
        normal = bm.faces[face_index].normal
        result = (normal.x, normal.y, normal.z)
        
        bm.free()
        return result
    
    #エッジ数を取得
    def count_edges(self, object_name: str) -> int:
        edges = self.get_object(object_name).data.edges
        return len(edges)

    #エッジの両端頂点取得
    def get_edge_vertices(self, object_name: str, edge_index: int):
        mesh = self.get_object(object_name).data
        edge = mesh.edges[edge_index]
        v1_idx, v2_idx = edge.vertices[0], edge.vertices[1]
        return v1_idx, v2_idx

    #指定頂点から隣接頂点へのエッジベクトルを取得
    def get_vertex_edge_vectors(self, object_name: str, vertex_index: int) -> list[tuple[float, float, float]]:
        mesh = self.get_object(object_name).data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.verts.ensure_lookup_table()
        
        vertex = bm.verts[vertex_index]
        edge_vectors = []
        
        # 頂点に接続する全エッジを取得
        for edge in vertex.link_edges:
            # エッジの両端の頂点を取得
            v1, v2 = edge.verts
            
            # 現在の頂点から隣接頂点への方向ベクトル
            if v1.index == vertex_index:
                direction = v2.co - v1.co
            else:
                direction = v1.co - v2.co
            
            edge_vectors.append((direction.x, direction.y, direction.z))
        
        bm.free()
        return edge_vectors
    
#=============================================================================================   
#メッシュ操作

    #エッジ分割
    def subdivide_edge(self, object_name: str, edge_index: int, cuts=1) -> int:
        mesh = self.get_object(object_name).data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.edges.ensure_lookup_table()
        bmesh.ops.subdivide_edges(bm, edges=[bm.edges[edge_index]], cuts=cuts)
        bm.to_mesh(mesh)
        bm.free()
        return self.count_vertex(object_name) - cuts

    #頂点の移動
    def move_vertex(self, object_name: str, vertex_index: int, x: float, y: float, z: float) -> None:
        mesh = self.get_object(object_name).data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.verts.ensure_lookup_table()
        bm.verts[vertex_index].co.x = x
        bm.verts[vertex_index].co.y = y
        bm.verts[vertex_index].co.z = z
        bm.to_mesh(mesh)
        bm.free()

    #頂点削除
    def delete_vertex(self, object_name: str, vertex_index: int,):
        mesh = self.get_object(object_name).data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.verts.ensure_lookup_table()
        bmesh.ops.delete(bm, geom=[bm.verts[vertex_index]], context="VERTS")
        bm.to_mesh(mesh)
        bm.free()

#=============================================================================================   
#ビスマス骸晶用

    #二面角
    def calculate_dihedral_angle(self, normal1: tuple, normal2: tuple) -> float:
        dot_product = sum(n1 * n2 for n1, n2 in zip(normal1, normal2))
        dot_product = max(-1.0, min(1.0, dot_product))
        angle_rad = math.acos(dot_product)
        angle_deg = math.degrees(angle_rad)
        return angle_rad
    
    #凸頂点の判定
    def is_convex_vertex(self, object_name: str, vertex_index: int) -> bool:
        mesh = self.get_object(object_name).data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.verts.ensure_lookup_table()
        
        vertex = bm.verts[vertex_index]
        
        # すべてのエッジの二面角をチェック
        is_convex = all(
            edge.calc_face_angle_signed() > 0 
            for edge in vertex.link_edges 
            if len(edge.link_faces) == 2
        )
        
        bm.free()
        return is_convex

    #すべての頂点から凸頂点を抽出
    def get_convex_vertices(self, object_name: str) -> list[int]:
        convex_vertices = []
        vertex_count = self.count_vertex(object_name)
        
        for vertex_idx in range(vertex_count):
            if self.is_convex_vertex(object_name, vertex_idx):
                convex_vertices.append(vertex_idx)
        
        return convex_vertices

    #ベクトルの長さを計算
    def vector_length(self, vector: tuple[float, float, float]) -> float:
        x, y, z = vector
        return math.sqrt(x**2 + y**2 + z**2)

    #指定方向側の頂点を取得
    def get_vertices_in_direction(self, object_name: str, direction: tuple[float, float, float]) -> list[int]:
        mesh = self.get_object(object_name).data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.verts.ensure_lookup_table()

        # オブジェクトの中心座標を計算
        center_x = sum(v.co.x for v in bm.verts) / len(bm.verts)
        center_y = sum(v.co.y for v in bm.verts) / len(bm.verts)
        center_z = sum(v.co.z for v in bm.verts) / len(bm.verts)

        direction_verts = []
        dx, dy, dz = direction

        for vert in bm.verts:
            # 中心から頂点へのベクトル
            to_vert_x = vert.co.x - center_x
            to_vert_y = vert.co.y - center_y
            to_vert_z = vert.co.z - center_z
            
            # 内積を計算、正なら成長方向側
            dot_product = to_vert_x * dx + to_vert_y * dy + to_vert_z * dz
            if dot_product > 0:
                direction_verts.append(vert.index)

        bm.free()
        return direction_verts

    #立方体をベクトル方向に伸長
    def stretch_cube_along_vector(self, object_name: str, vector: tuple[float, float, float], max_distance: float):
        
        # 成長方向側の頂点を取得
        direction_verts = self.get_vertices_in_direction(object_name, vector)
        
        vx, vy, vz = vector
        
        # 成長方向側の頂点のみを移動
        for v_idx in direction_verts:
            x, y, z = self.locate_vertex(object_name, v_idx)
            
            # ベクトル方向に max_distance だけ移動
            new_x = x + vx * max_distance
            new_y = y + vy * max_distance
            new_z = z + vz * max_distance
            
            self.move_vertex(object_name, v_idx, new_x, new_y, new_z)

#=============================================================================================   
#アニメーション

    #キーフレーム挿入
    def insert_keyframe(self, object_name: str, frame_index: int):
        object = self.get_object(object_name)
        object.keyframe_insert(data_path="location", frame=frame_index)

    #シェイプキー追加
    def add_shape_key(self, object_name: str):
        object = self.get_object(object_name)
        object.shape_key_add(from_mix=False)
        object.active_shape_key_index = len(self.get_shape_keys(object_name)) - 1

    #シェイプキー一覧取得
    def get_shape_keys(self, object_name: str):
        return self.get_object(object_name).data.shape_keys.key_blocks

    
