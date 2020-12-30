import os


def create_save_path(path):
    if not os.path.exists('saves'):
        os.mkdir('saves')
    
    savedir = os.path.join('saves', path)
    
    if not os.path.exists(savedir):
        os.mkdir(savedir)
    else:
        for file in ('world.tworld', 'world.meta', 'world.entities'):
            savefile = os.path.join(savedir, file)
            if os.path.exists(savefile):
                os.remove(savefile)


def check_save_path(path):
    return os.path.exists(os.path.join('saves', path, 'world.tworld'))
