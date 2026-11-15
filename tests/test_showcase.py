import json
from scripts import export_showcase


def test_export_preserves_existing_examples(monkeypatch, tmp_path):
    data = tmp_path/'data'
    monkeypatch.setattr(export_showcase, 'DATA', data)
    monkeypatch.setattr(export_showcase, 'ROOT', tmp_path)
    for identifier in ['a'*32,'b'*32]:
        folder = data/identifier
        folder.mkdir(parents=True)
        frames = []
        for i in range(2):
            (folder/f'{i}.png').write_bytes(b'preview fixture')
            frames.append({'image':f'/artifacts/{identifier}/{i}.png'})
        (folder/'manifest.json').write_text(json.dumps({'status':'ready','id':identifier,
            'query':{'ra':10,'dec':20,'fov':5},'frames':frames}))
        export_showcase.export(identifier)
    index = json.loads((tmp_path/'frontend/public/showcase/index.json').read_text())
    assert [item['id'] for item in index] == ['a'*32,'b'*32]
    assert all(item['frames'] == 2 for item in index)
