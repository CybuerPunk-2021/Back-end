from os.path import exists
path = "D:\\darak\\image\\"

def check_profile_image_exist(uid):
    return exists(path + 'profile\\' + str(uid))

def read_profile_image(uid):
    if check_profile_image_exist(uid):
        f = open(path + 'profile\\' + str(uid), 'rb')
        image = f.read()
        f.close()
        return image
    else:
        return False

def write_profile_image(uid, data):
    try:
        f = open(path + 'profile\\' + str(uid), 'wb')
        f.write(data)
        f.close()
        return True
    else:
        return False

