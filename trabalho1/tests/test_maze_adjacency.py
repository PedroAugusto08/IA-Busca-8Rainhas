import pytest
from pathlib import Path
from trabalho1.src.maze import Maze

# Helpers

def write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content.strip() + "\n", encoding="utf-8")
    return p


def test_parsing_sucesso(tmp_path):
    # Grid 2x3 (2 linhas, 3 colunas)
    # Bits: N S E W
    content = """
    1010S 1111 0101
    0001 1000G 0110
    """
    f = write(tmp_path, "maze.txt", content)
    mz = Maze.from_file(f)
    assert mz.start() == (0,0)
    assert mz.goal() == (1,1)

    # Verifica alguns vizinhos manualmente
    # (0,0) tem 1010 -> N=1 (ignorado lim), S=0, E=1, W=0 => deve permitir (0,1) apenas
    assert list(mz.neighbors((0,0))) == [(0,1)]
    # (0,1) tem 1111 -> pode ir N (ignora), S=(1,1), E=(0,2), W=(0,0)
    neigh_01 = list(mz.neighbors((0,1)))
    assert set(neigh_01) == {(1,1),(0,2),(0,0)}

    # passable: (1,0) tem 0001 -> tem W=1 então é passável
    assert mz.passable((1,0)) is True


def test_token_invalido_bits(tmp_path):
    content = """
    10A0S 1111 0101
    0001 1000G 0110
    """
    f = write(tmp_path, "maze_inv.txt", content)
    with pytest.raises(ValueError):
        Maze.from_file(f)


def test_token_invalido_tamanho(tmp_path):
    content = """
    101S 1111 0101
    0001 1000G 0110
    """
    f = write(tmp_path, "maze_inv2.txt", content)
    with pytest.raises(ValueError):
        Maze.from_file(f)


def test_multiplos_start_ausencia_goal(tmp_path):
    content = """
    1010S 1111S 0101
    0001 1000 0110
    """
    f = write(tmp_path, "maze_inv3.txt", content)
    with pytest.raises(ValueError):
        Maze.from_file(f)

    content2 = """
    1010 1111 0101
    0001 1000 0110
    """
    f2 = write(tmp_path, "maze_inv4.txt", content2)
    with pytest.raises(ValueError):
        Maze.from_file(f2)


def test_render_path(tmp_path):
    content = """
    1010S 1111 0101
    0001 1000G 0110
    """
    f = write(tmp_path, "maze_render.txt", content)
    mz = Maze.from_file(f)
    path = [(0,0),(0,1),(1,1)]  # S -> (0,1) -> G
    rendered = mz.render_path(path)
    # Verifica presença de S, G e 'o'
    assert 'S' in rendered and 'G' in rendered and 'o' in rendered
