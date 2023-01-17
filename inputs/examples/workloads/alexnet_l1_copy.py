workload = {
    0: {  # conv1, stride 2
        'equation': 'O[b][k][oy][ox]+=W[k][c][fy][fx]*I[b][c][ix][iy]',
        'dimension_relations': ['ix=1*ox+1*fx', 'iy=1*oy+1*fy'], # Sx=1 Sx=1 Px=1 Py=1
        'loop_dim_size': {'B': 1, 'K': 96, 'C': 3, 'OY': 56, 'OX': 56, 'FY': 11, 'FX': 11},
        'operand_precision': {'O': 16, 'O_final': 8, 'W': 8, 'I': 8},
        'operand_source': {'W': [], 'I': []},
        'constant_operands': ['W'],
        'core_allocation': 1,
        'temporal_mapping': {'I': [[('K', 2), ('FX', 11), ('K', 8), ('OY', 1)], [('OX', 56), ('K', 3)], [('C', 3), ('OY', 8)]], 'W': [[('K', 2), ('FX', 11), ('K', 8)], [('OY', 1), ('OX', 56), ('K', 3), ('C', 3), ('OY', 8)]], 'O': [[('K', 2)], [('FX', 11), ('K', 8), ('OY', 1), ('OX', 56), ('K', 3)], [('C', 3), ('OY', 8)]]},
		'spatial_mapping': {'D1': ('K', 2), 'D2': ('OY', 7), 'D3': ('FY', 11)},
		'memory_operand_links': {'O': 'O', 'W': 'I2', 'I': 'I1'}
    }
}

