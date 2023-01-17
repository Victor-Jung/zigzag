workload = {
    0: {  # conv1, stride 2
        'equation': 'O[b][k][oy][ox]+=W[k][c][fy][fx]*I[b][c][ix][iy]',
        'dimension_relations': ['ix=2*ox+1*fx', 'iy=2*oy+1*fy'], # Sx=2 Sx=2 Px=1 Py=1
        'loop_dim_size': {'B': 1, 'K': 64, 'C': 3, 'OY': 112, 'OX': 112, 'FY': 7, 'FX': 7},
        'operand_precision': {'O': 16, 'O_final': 8, 'W': 8, 'I': 8},
        'operand_source': {'W': [], 'I': []},
        'constant_operands': ['W'],
        'core_allocation': 1,
        'spatial_mapping': {'D1': ('K', 16), 'D2': ('C', 3)},
        'temporal_ordering': [('OX', 54), ('OY', 54), ('FX', 11), ('FY', 11), ('K', 6)],
        'temporal_mapping': {'O': [[], [('OX', 54), ('OY', 54), ('FX', 11), ('FY', 11)], [('K', 6)]], 
                             'W': [[('OX', 54), ('OY', 54), ('FX', 11), ('FY', 11)], [('K', 6)]], 
                             'I': [[], [('OX', 54), ('OY', 54), ('FX', 11), ('FY', 11), ('K', 6)], []]
                            },
        'memory_operand_links': {'O': 'O', 'W': 'I2', 'I': 'I1'}
    }
}

