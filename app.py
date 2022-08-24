from aiohttp import web
from application_settings import credentials
import datetime
import aiofiles
from helpers import read_exel
from models import db, File, User


async def write_file(file_obj, file_parts):
    today = datetime.datetime.today()
    file_name = file_parts.split('.')[0]
    file_name = (
            file_name + '-'
            + str(today).replace(':', '-').replace(' ', '-')
            + '.xlsx'
    )
    async with aiofiles.open(file_name, mode='wb') as f:
        await f.write(file_obj)
    number = read_exel(file_name=file_name)
    return number


async def get_user_files(request):
    user_name = request.match_info.get('user')
    with db:
        users = User.select().where(User.name == user_name)
    user_list = [user.name for user in users]
    if not user_list:
        data = {'status': 'failed', 'reason': 'There is no such user.'}
        return web.json_response(data=data, status=400)
    else:
        with db:
            files = File.select(File.file_name).where(File.user_name == user_name)
        res = [file.file_name for file in files]
        if res:
            data = {files: res, 'status': 'success'}
            return web.json_response(data=data, status=200)
        else:
            data = {'message': 'This user has no files yet.'}
            return web.json_response(data=data, status=200)


async def handler_post(request):
    access_password = request.headers.get('Access-Password')
    if access_password != credentials.get('password'):
        return web.HTTPUnauthorized(reason='Password denied')
    else:
        # print(request.headers['Content-Type'])
        if 'multipart/form-data' not in request.headers['Content-Type']:
            data = {
                'status': 'failed',
                'reason': 'The Content-Type must be: -- multipart/form-data'
            }
            return web.json_response(data=data, status=400)
        reader = await request.multipart()
        field = await reader.next()
        filename = field.filename
        if not filename:
            data = {
                'status': 'failed',
                'reason': 'Your file is empty'
            }
            return web.json_response(data=data, status=400)
        filename_parts = filename.split('.')
        extension = filename_parts[-1]
        if extension != 'xlsx':
            data = {'status': 'failed', 'reason': 'The API works with exel files only!'}
            return web.json_response(data=data, status=400)
        else:
            user_name = request.match_info.get('user')
            try:
                with db:
                    File.create(filename=filename, user_name=user_name)
            except Exception:
                data = {
                    'status': 'failed',
                    'reason': f'User {user_name} already have file {filename}'
                }
                return web.json_response(data=data, status=400)
            file = await field.read(decode=True)
            try:
                value = await write_file(
                    file_obj=file,
                    file_parts=filename
                )
            except ValueError as e:
                data = {'status': 'failed', 'Failure descriptions': str(e)}
                return web.json_response(data=data, status=400)
            else:
                data = {
                    'status': 'success',
                    'value': value
                }
                return web.json_response(data=data, status=201)


if __name__ == '__main__':
    app = web.Application()
    app.router.add_get('/user-files/{user}', get_user_files)
    app.router.add_post('/upload/{user}', handler_post)
    web.run_app(app, host='127.0.0.1', port=8080)