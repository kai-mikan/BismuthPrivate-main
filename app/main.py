from blender import Blender
import math, bmesh

def animation():
    blender = Blender()
    print("Before", blender.all_objects())
    # キューブを 2 こ追加
    cube_names = [blender.add_cube(0, 0, 0), blender.add_cube(1, 1, 1)]
    print("After", blender.all_objects())

    # 最初の状態を 1番フレームとして保存
    blender.insert_keyframe(cube_names[0], 1)
    # 1番目のキューブを x 方向に +1 だけ移動
    x, y, z = blender.locate_object(cube_names[0])
    blender.move_object(cube_names[0], x + 1, y, z)
    # 移動後の状態を 10番フレームとして保存
    blender.insert_keyframe(cube_names[0], 10)

    blender.save_scene("/app/animation.blend")

def edit():
    blender = Blender()
    cube_name = blender.add_cube(0, 0, 0)
    # 編集前の頂点・辺を表示
    for vertex_idx in range(blender.count_vertex(cube_name)):
        x, y, z = blender.locate_vertex(cube_name, vertex_idx)
        print(f"Vertex {vertex_idx}: Coordinates ({x},{y},{z})")
    for edge_idx in range(blender.count_edges(cube_name)):
        v1_idx, v2_idx = blender.get_edge_vertices(cube_name, edge_idx)
        print(f"Edge {edge_idx}: Connecting ({v1_idx}, {v2_idx})")
    # 編集前の画像を保存
    blender.render("/app/editBefore.png")

    # 0 番の辺を細分化することで新たな頂点を作成
    new_vertex_idx = blender.subdivide_edge(cube_name, 0)
    print("New Vertex", new_vertex_idx)
    # 新たな頂点を移動
    vx, vy, vz = blender.locate_vertex(cube_name, new_vertex_idx)
    blender.move_vertex(cube_name, new_vertex_idx, vx, vy, vz - 10)

    # 編集後の頂点・辺を表示
    for vertex_idx in range(blender.count_vertex(cube_name)):
        x, y, z = blender.locate_vertex(cube_name, vertex_idx)
        print(f"Vertex {vertex_idx}: Coordinates ({x},{y},{z})")
    for edge_idx in range(blender.count_edges(cube_name)):
        v1_idx, v2_idx = blender.get_edge_vertices(cube_name, edge_idx)
        print(f"Edge {edge_idx}: Connecting ({v1_idx}, {v2_idx})")
    # 編集後の画像を保存
    blender.render("/app/editAfter.png")

    blender.save_scene("/app/edit.blend")

def test_convex_detection():
    """凸頂点検出の完全テスト"""
    blender = Blender()
    cube_name = blender.add_cube(0, 0, 0)
    
    print("\n" + "="*50)
    print("=== Convex Vertex Detection Test ===")
    print("="*50 + "\n")
    
    print(f"Total vertices: {blender.count_vertex(cube_name)}")
    
    # 凸頂点を抽出
    convex_verts = blender.get_convex_vertices(cube_name)
    print(f"\nConvex vertices: {convex_verts}")
    print(f"Count: {len(convex_verts)}/{blender.count_vertex(cube_name)}")
    
    # 各凸頂点の座標を表示
    print("\nConvex vertex positions:")
    for idx in convex_verts:
        x, y, z = blender.locate_vertex(cube_name, idx)
        print(f"  Vertex {idx}: ({x:6.2f}, {y:6.2f}, {z:6.2f})")
    
    # 判定結果の検証
    if len(convex_verts) == 8:
        print("\n✅ SUCCESS: All 8 corners detected as convex!")
    else:
        print(f"\n❌ ERROR: Expected 8 convex vertices, got {len(convex_verts)}")
    
    # 凸頂点を可視化（少し外側に移動）
    print("\nVisualizing convex vertices...")
    for idx in convex_verts:
        x, y, z = blender.locate_vertex(cube_name, idx)
        blender.move_vertex(cube_name, idx, x * 1.3, y * 1.3, z * 1.3)
    
    blender.render("/app/convex_test.png")
    blender.save_scene("/app/convex_test.blend")
    print("✓ Saved: /app/convex_test.png")
    print("✓ Saved: /app/convex_test.blend")

def test_convex_detection_dramatic():
    """凸頂点検出の劇的な可視化テスト"""
    blender = Blender()
    cube_name = blender.add_cube(0, 0, 0)
    
    print("\n" + "="*50)
    print("=== Dramatic Convex Vertex Visualization ===")
    print("="*50 + "\n")
    
    # 凸頂点を抽出
    convex_verts = blender.get_convex_vertices(cube_name)
    print(f"Convex vertices found: {len(convex_verts)}")
    
    # 編集前の画像
    blender.render("/app/before.png")
    print("✓ Saved: /app/before.png (original cube)")
    
    # 凸頂点を大きく外側に移動（2倍！）
    print("\nMoving convex vertices outward (2x)...")
    for idx in convex_verts:
        x, y, z = blender.locate_vertex(cube_name, idx)
        blender.move_vertex(cube_name, idx, x * 2.0, y * 2.0, z * 2.0)
    
    # 編集後の画像
    blender.render("/app/after.png")
    print("✓ Saved: /app/after.png (expanded corners)")
    
    blender.save_scene("/app/convex_dramatic.blend")
    print("✓ Saved: /app/convex_dramatic.blend")
    
    print("\n✅ Visualization complete!")

def test_concave_detection():
    """凹頂点も正しく判定できるかテスト"""
    blender = Blender()
    cube_name = blender.add_cube(0, 0, 0)
    
    print("\n" + "="*50)
    print("=== Concave Vertex Detection Test ===")
    print("="*50 + "\n")
    
    # エッジ0を分割して新しい頂点を作成
    new_vertex_idx = blender.subdivide_edge(cube_name, 0)
    print(f"Created new vertex {new_vertex_idx} by subdividing edge 0")
    
    # 新しい頂点を内側に移動（凹を作る）
    vx, vy, vz = blender.locate_vertex(cube_name, new_vertex_idx)
    blender.move_vertex(cube_name, new_vertex_idx, vx, vy, vz + 0.5)
    print(f"Moved vertex {new_vertex_idx} inward to create concave")
    
    # 編集前後の画像
    blender.render("/app/concave_test.png")
    
    # 凸頂点を抽出
    convex_verts = blender.get_convex_vertices(cube_name)
    total_verts = blender.count_vertex(cube_name)
    
    print(f"\nTotal vertices: {total_verts}")
    print(f"Convex vertices: {convex_verts}")
    print(f"Count: {len(convex_verts)}/{total_verts}")
    
    # 新しく作った頂点が凹と判定されているかチェック
    if new_vertex_idx not in convex_verts:
        print(f"\n✅ SUCCESS: Vertex {new_vertex_idx} correctly identified as CONCAVE!")
    else:
        print(f"\n❌ ERROR: Vertex {new_vertex_idx} incorrectly identified as convex")
    
    # 元の8頂点は凸のままか？
    original_convex = [v for v in convex_verts if v < 8]
    if len(original_convex) == 8:
        print("✅ SUCCESS: All 8 original corners still convex!")
    else:
        print(f"❌ ERROR: Only {len(original_convex)} original corners detected as convex")
    
    blender.save_scene("/app/concave_test.blend")
    print("\n✓ Saved: /app/concave_test.png")
    print("✓ Saved: /app/concave_test.blend")

def test_concave_detection_fixed():
    """確実に凹を作ってテスト"""
    blender = Blender()
    cube_name = blender.add_cube(0, 0, 0)
    
    print("\n" + "="*50)
    print("=== Fixed Concave Vertex Detection Test ===")
    print("="*50 + "\n")
    
    # エッジ0を分割
    new_vertex_idx = blender.subdivide_edge(cube_name, 0)
    vx, vy, vz = blender.locate_vertex(cube_name, new_vertex_idx)
    
    print(f"Original vertex {new_vertex_idx} position: ({vx:.2f}, {vy:.2f}, {vz:.2f})")
    
    # 大きく内側に移動（立方体の中心方向）
    # 中心は(0, 0, 0)なので、座標を0.5倍すれば中心寄りになる
    blender.move_vertex(cube_name, new_vertex_idx, vx * 0.5, vy * 0.5, vz * 0.5)
    
    new_x, new_y, new_z = blender.locate_vertex(cube_name, new_vertex_idx)
    print(f"Moved to: ({new_x:.2f}, {new_y:.2f}, {new_z:.2f})")
    
    # 編集前後の画像
    blender.render("/app/concave_fixed.png")
    
    # 凸頂点を抽出
    convex_verts = blender.get_convex_vertices(cube_name)
    total_verts = blender.count_vertex(cube_name)
    
    print(f"\nTotal vertices: {total_verts}")
    print(f"Convex vertices: {convex_verts}")
    print(f"Concave vertices: {[i for i in range(total_verts) if i not in convex_verts]}")
    
    # 判定
    if new_vertex_idx not in convex_verts:
        print(f"\n✅ SUCCESS: Vertex {new_vertex_idx} correctly identified as CONCAVE!")
    else:
        print(f"\n❌ ERROR: Vertex {new_vertex_idx} still identified as convex")
        print("   Debugging needed...")
    
    blender.save_scene("/app/concave_fixed.blend")

def debug_vertex_8():
    """頂点8の詳細を調べる"""
    blender = Blender()
    cube_name = blender.add_cube(0, 0, 0)
    
    # エッジ0を分割
    new_vertex_idx = blender.subdivide_edge(cube_name, 0)
    vx, vy, vz = blender.locate_vertex(cube_name, new_vertex_idx)
    blender.move_vertex(cube_name, new_vertex_idx, vx, vy, vz + 0.5)
    
    print(f"\n=== Debug Vertex {new_vertex_idx} ===\n")
    
    mesh = blender.get_object(cube_name).data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    
    vertex = bm.verts[new_vertex_idx]
    
    print(f"Position: ({vx:.2f}, {vy:.2f}, {vz + 0.5:.2f})")
    print(f"Connected edges: {len(vertex.link_edges)}")
    print(f"Connected faces: {len(vertex.link_faces)}")
    
    print("\nEdge angles:")
    for edge in vertex.link_edges:
        num_faces = len(edge.link_faces)
        print(f"  Edge {edge.index}: {num_faces} faces", end="")
        if num_faces == 2:
            angle = edge.calc_face_angle_signed()
            angle_deg = math.degrees(angle)
            print(f" → {angle:.4f} rad ({angle_deg:.2f}°)")
        else:
            print(" → BOUNDARY (skipped)")
    
    bm.free()

def test_concave_simple():
    """シンプルに凹を作る"""
    blender = Blender()
    cube_name = blender.add_cube(0, 0, 0)
    
    print("\n=== Simple Concave Test ===\n")
    
    # エッジ0を分割
    new_vertex_idx = blender.subdivide_edge(cube_name, 0)
    vx, vy, vz = blender.locate_vertex(cube_name, new_vertex_idx)
    
    print(f"Original: ({vx:.2f}, {vy:.2f}, {vz:.2f})")
    
    # 中心(0,0,0)に向かって移動
    blender.move_vertex(cube_name, new_vertex_idx, vx * 0.5, vy * 0.5, vz * 0.5)
    
    new_pos = blender.locate_vertex(cube_name, new_vertex_idx)
    print(f"Moved to: ({new_pos[0]:.2f}, {new_pos[1]:.2f}, {new_pos[2]:.2f})")
    
    # 判定
    is_convex = blender.is_convex_vertex(cube_name, new_vertex_idx)
    print(f"\nVertex {new_vertex_idx} is: {'CONVEX ❌' if is_convex else 'CONCAVE ✅'}")
    
    blender.render("/app/simple_concave.png")
    blender.save_scene("/app/simple_concave.blend")

def test_suzanne_convex():
    """スザンヌで凸頂点検出テスト"""
    blender = Blender()
    suzanne_name = blender.add_suzanne(0, 0, 0)
    
    print("\n=== Suzanne Convex Vertex Detection ===\n")
    
    total_vertices = blender.count_vertex(suzanne_name)
    print(f"Total vertices: {total_vertices}")
    
    # 凸頂点を抽出
    convex_verts = blender.get_convex_vertices(suzanne_name)
    print(f"Convex vertices: {len(convex_verts)}")
    print(f"Ratio: {len(convex_verts)}/{total_vertices} ({len(convex_verts)/total_vertices*100:.1f}%)")
    
    # 最初の10個の凸頂点の座標を表示
    print(f"\nFirst 10 convex vertex positions:")
    for idx in convex_verts[:10]:
        x, y, z = blender.locate_vertex(suzanne_name, idx)
        print(f"  Vertex {idx}: ({x:.2f}, {y:.2f}, {z:.2f})")
    
    if len(convex_verts) > 10:
        print(f"  ... and {len(convex_verts) - 10} more")
    
    # 凸頂点を可視化（少し外側に移動）
    print("\nVisualizing convex vertices...")
    for idx in convex_verts:
        x, y, z = blender.locate_vertex(suzanne_name, idx)
        # 原点からの方向に少し移動
        scale = 1.1
        blender.move_vertex(suzanne_name, idx, x * scale, y * scale, z * scale)
    
    blender.render("/app/suzanne_convex_test.png")
    blender.save_scene("/app/suzanne_convex_test.blend")
    
    print("\n✓ Saved: /app/suzanne_convex_test.png")
    print("✓ Convex vertices are slightly enlarged in the render")

def test_edge_vectors():
    """エッジベクトルのテスト"""
    blender = Blender()
    cube_name = blender.add_cube(0, 0, 0)
    
    print("\n=== Edge Vector Test ===\n")
    
    # 頂点0のエッジベクトルを取得
    vertex_idx = 0
    x, y, z = blender.locate_vertex(cube_name, vertex_idx)
    print(f"Vertex {vertex_idx}: ({x:.2f}, {y:.2f}, {z:.2f})")
    
    edge_vectors = blender.get_vertex_edge_vectors(cube_name, vertex_idx)
    print(f"\nEdge vectors from vertex {vertex_idx}:")
    
    for i, (ex, ey, ez) in enumerate(edge_vectors):
        print(f"  Vector {i}: ({ex:6.3f}, {ey:6.3f}, {ez:6.3f})")
        # ベクトルの長さを確認（正規化されているので1のはず）
        length = math.sqrt(ex**2 + ey**2 + ez**2)
        print(f"    Length: {length:.6f}")
    
    print(f"\nTotal edge vectors: {len(edge_vectors)}")

def test_vector_length():
    """ベクトル長さ計算のテスト"""
    blender = Blender()
    
    print("\n=== Vector Length Test ===\n")
    
    # テストベクトル
    vectors = [
        (1, 0, 0),      # 長さ1
        (0, 1, 0),      # 長さ1
        (1, 1, 0),      # 長さ√2
        (1, 1, 1),      # 長さ√3
        (3, 4, 0),      # 長さ5
    ]
    
    for vec in vectors:
        length = blender.vector_length(vec)
        print(f"Vector {vec}: length = {length:.4f}")

def test_scale():
    """スケール変更のテスト"""
    blender = Blender()
    
    print("\n=== Scale Test ===\n")
    
    # 3つの立方体を配置
    cube1 = blender.add_cube(-3, 0, 0)
    cube2 = blender.add_cube(0, 0, 0)
    cube3 = blender.add_cube(3, 0, 0)
    
    # それぞれ異なるスケールを適用
    blender.scale_object_uniform(cube1, 0.5)  # 半分
    blender.scale_object(cube2, 0.5, 1.0, 1.5)  # 非均一
    blender.scale_object_uniform(cube3, 1.5)  # 1.5倍
    
    print(f"Cube1: scale = 0.5 (uniform)")
    print(f"Cube2: scale = (0.5, 1.0, 1.5) (non-uniform)")
    print(f"Cube3: scale = 1.5 (uniform)")
    
    blender.render("/app/scale_test.png")
    blender.save_scene("/app/scale_test.blend")
    
    print("\n✓ Saved: /app/scale_test.png")

def test_boolean_union():
    """ブーリアン統合のテスト"""
    blender = Blender()
    
    print("\n=== Boolean Union Test ===\n")
    
    # 2つの立方体を少し重ねて配置
    cube1 = blender.add_cube(0, 0, 0)
    cube2 = blender.add_cube(1, 0, 0)  # X方向に1ユニットずらす
    
    print(f"Before union:")
    print(f"  Total objects: {len(blender.all_objects())}")
    print(f"  Cube1: {cube1}")
    print(f"  Cube2: {cube2}")
    
    # レンダリング（統合前）
    blender.render("/app/boolean_before.png")
    
    # ブーリアン統合
    result = blender.boolean_union(cube1, cube2)
    
    print(f"\nAfter union:")
    print(f"  Total objects: {len(blender.all_objects())}")
    print(f"  Result: {result}")
    print(f"  Vertices: {blender.count_vertex(result)}")
    
    # レンダリング（統合後）
    blender.render("/app/boolean_after.png")
    blender.save_scene("/app/boolean_test.blend")
    
    print("\n✓ Saved: /app/boolean_after.png")

def test_boolean_multiple():
    """複数オブジェクトのブーリアン統合テスト"""
    blender = Blender()
    
    print("\n=== Multiple Boolean Union Test ===\n")
    
    # 基準となる立方体
    base = blender.add_cube(0, 0, 0)
    
    # 6つの小さな立方体を各面に配置
    cubes = []
    positions = [
        (1.5, 0, 0),   # +X
        (-1.5, 0, 0),  # -X
        (0, 1.5, 0),   # +Y
        (0, -1.5, 0),  # -Y
        (0, 0, 1.5),   # +Z
        (0, 0, -1.5),  # -Z
    ]
    
    for x, y, z in positions:
        cube = blender.add_cube(x, y, z)
        blender.scale_object_uniform(cube, 0.5)  # 小さくする
        cubes.append(cube)
    
    print(f"Created {len(cubes)} small cubes")
    print(f"Total objects before union: {len(blender.all_objects())}")
    
    # レンダリング（統合前）
    blender.render("/app/boolean_multi_before.png")
    
    # 全て統合
    result = blender.boolean_union_multiple(base, cubes)
    
    print(f"\nAfter union:")
    print(f"  Result: {result}")
    print(f"  Total objects: {len(blender.all_objects())}")
    print(f"  Vertices: {blender.count_vertex(result)}")
    
    # レンダリング（統合後）
    blender.render("/app/boolean_multi_after.png")
    blender.save_scene("/app/boolean_multi_test.blend")
    
    print("\n✓ Saved: /app/boolean_multi_after.png")

def test_step1_direction_vertices():
    """ステップ1: 方向側の頂点取得テスト"""
    blender = Blender()
    
    print("\n=== Step 1: Get Vertices in Direction ===\n")
    
    # 立方体を配置
    cube = blender.add_cube(0, 0, 0)
    
    print(f"Total vertices: {blender.count_vertex(cube)}")
    print("\nTesting different directions:\n")
    
    # 各方向でテスト
    directions = [
        (1, 0, 0, "+X"),
        (-1, 0, 0, "-X"),
        (0, 1, 0, "+Y"),
        (0, -1, 0, "-Y"),
        (0, 0, 1, "+Z"),
        (0, 0, -1, "-Z"),
    ]
    
    for dx, dy, dz, label in directions:
        direction = (dx, dy, dz)
        verts = blender.get_vertices_in_direction(cube, direction)
        
        print(f"{label} direction {direction}:")
        print(f"  Vertices: {verts}")
        print(f"  Count: {len(verts)}")
        
        # 各頂点の座標も表示
        print(f"  Coordinates:")
        for v_idx in verts:
            x, y, z = blender.locate_vertex(cube, v_idx)
            print(f"    Vertex {v_idx}: ({x:5.2f}, {y:5.2f}, {z:5.2f})")
        print()
    
    blender.save_scene("/app/step1_test.blend")
    print("✓ Test complete!")

def test_step2_stretch():
    """ステップ2: 伸長機能のテスト"""
    blender = Blender()
    
    print("\n=== Step 2: Stretch Cube ===\n")
    
    # 立方体を配置
    cube = blender.add_cube(0, 0, 0)
    blender.scale_object_uniform(cube, 0.5)  # 小さくする
    
    print(f"Original cube:")
    print(f"  Vertices: {blender.count_vertex(cube)}")
    
    # レンダリング（伸長前）
    blender.render("/app/step2_before.png")
    
    # X方向に伸長
    direction = (1, 0, 0)  # X軸方向（正規化済み）
    max_distance = 2.0
    
    print(f"\nStretching:")
    print(f"  Direction: {direction}")
    print(f"  Distance: {max_distance}")
    
    # 伸長実行
    blender.stretch_cube_along_vector(cube, direction, max_distance)
    
    print(f"\nAfter stretch:")
    print(f"  Vertices: {blender.count_vertex(cube)}")
    
    # 頂点座標を確認
    print(f"\nVertex coordinates after stretch:")
    for v_idx in range(blender.count_vertex(cube)):
        x, y, z = blender.locate_vertex(cube, v_idx)
        print(f"  Vertex {v_idx}: ({x:6.2f}, {y:6.2f}, {z:6.2f})")
    
    # レンダリング（伸長後）
    blender.render("/app/step2_after.png")
    blender.save_scene("/app/step2_test.blend")
    
    print("\n✓ Saved: /app/step2_after.png")

def test_step2_multiple_directions():
    """ステップ2: 複数方向への伸長テスト"""
    blender = Blender()
    
    print("\n=== Step 2: Multiple Directions ===\n")
    
    # 3つの立方体を配置して、それぞれ異なる方向に伸長
    positions = [
        (-2, 0, 0, (1, 0, 0), 1.5, "+X"),
        (2, 0, 0, (0, 1, 0), 1.0, "+Y"),
        (0, 0, 2, (0, 0, -1), 2.0, "-Z"),
    ]
    
    for px, py, pz, direction, distance, label in positions:
        cube = blender.add_cube(px, py, pz)
        blender.scale_object_uniform(cube, 0.3)
        blender.stretch_cube_along_vector(cube, direction, distance)
        print(f"Stretched cube at ({px}, {py}, {pz}) in {label} direction by {distance}")
    
    blender.render("/app/step2_multi.png")
    blender.save_scene("/app/step2_multi_test.blend")
    
    print("\n✓ Saved: /app/step2_multi.png")

if __name__ == "__main__":

    #テスト用

    #animation()  # オブジェクト単位でのアニメーションをテスト
    #edit()  # オブジェクトの頂点編集をテスト
    #test_convex_detection()
    #test_convex_detection_dramatic()
    #test_concave_detection()
    #test_concave_detection_fixed()
    #debug_vertex_8()
    #test_concave_simple()
    #test_suzanne_convex()
    #test_edge_vectors()
    #test_vector_length()
    #test_scale()
    #test_boolean_union()
    #test_boolean_multiple()
    #test_step1_direction_vertices()
    test_step2_stretch()
    test_step2_multiple_directions()