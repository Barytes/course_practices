"""注意力。按第 5 → 6 → 7 → 8 → 9 章的顺序往同一个 Attention 类里加零件。"""

# 第 5 章：TinyAttention（可先写在上级目录 attention.py 草稿里，再迁过来）
# 第 6 章：改成 CausalAttention，加上因果掩码和键值缓存
# 第 7 章：改成分组查询（q/k/v 宽度不同 + repeat_kv）
# 第 8 章：在拼接缓存之前旋转 Q、K
# 第 9 章：QK-Norm + SDPA 分支，类名定为 Attention，与官方对齐
