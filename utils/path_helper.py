from pathlib import Path


def find_dir(target_name: str) -> Path:
    '''
    현재 파일의 위치를 기준으로 상위 디렉토리를 탐색하여 지정된 이름의 디렉토리를 찾는 함수

    :param target_name: 찾을 디렉토리 이름
    :return: 찾은 디렉토리의 Path 객체
    '''
    path = Path(__file__).resolve()
    for parent in path.parents:
        if parent.name == target_name:
            return parent
    raise RuntimeError(f"프로젝트 루트 '{target_name}'을 찾을 수 없음.")