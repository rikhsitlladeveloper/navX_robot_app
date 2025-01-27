## Installation
```sh
git clone https://github.com/rikhsitlladeveloper/navX_robot_app
cd navX_robot_app
pip3 install -r requirements.txt
```

## Development
##### Run on development environment
---
```sh
cd navX_robot_app
sh ./devrun.sh
```
##### Run on production environment
---
```sh
cd navX_robot_app
sh ./prodrun.sh
```

# API usage

### Authorization: 
 - http Basic Auth 
## urls:
| Url                   | Method | Required Role |
|-----------------------|--------|---------------|
| /api/user/register    | POST   | admin         |
| /api/user/delete      | DELETE | admin         |
| /api/bringup/start    | GET    | admin         | 
| /api/bringup/stop     | POST   | admin         |
| /api/mapping/start    | GET    | admin         |
| /api/mapping/stop     | GET    | admin         |
| /api/mapping/savemap  | GET    | admin         |
| /api/mapping/getmap   | GET    | admin         |
| /api/mapping/loadmap  | POST   | admin         |
| /api/mapping/delete   | DELETE | admin         |
| /api/navigation/start | GET    | admin         |
| /api/navigation/stop  | GET    | admin         |
| /api/robot/reboot     | GET    | admin         |

## Response Fields:
```json
{
    "data": null,
    "error": false,
    "message": null
}
```

### /api/user/register
##### Request body
```json
{
    "username": "username",
    "password": "password",
    "role": "role"
}
```
##### Response
if everything OK
```json
{
    "data": {
        "username": "username"
    },
    "error": false,
    "message": "new user added"
}
```
if username used
```json
{
    "data": {
        "username": "username"
    },
    "error": true,
    "message": "user already exists"
}
```
if request body is wrong
```json
{
    "data": {
        "validation error": "error description"
    },
    "error": true,
    "message": "wrong request"
}
```

### /api/user/delete
##### Request body
```json
{
    "username": "username"
}
```
##### Response
if everything OK
```json
{
    "data": {
        "username": "username"
    },
    "error": false,
    "message": "deleted user"
}
```
if no user with requested username
```json
{
    "data": {
        "username": "username"
    },
    "error": false,
    "message": "no such user"
}
```
if request body is wrong
```json
{
    "data": {
        "validation error": "error description"
    },
    "error": true,
    "message": "wrong request"
}
```


### /api/bringup/start
##### Response
```json
{
    "data": {
        "launcher": "BRINGUP"
    },
    "error": false,
    "message": null
}
```

### /api/bringup/stop
##### Response
```json
{
    "data": {
        "launcher": "OFF"
    },
    "error": false,
    "message": null
}
```

### /api/mapping/start
##### Request body
```json
{
    "slam_method": "slam_method"
}
```
##### Response
if launcher is off
```json
{
    "data": {
        "launcher": "OFF"
    },
    "error": true,
    "message": "first launch bringup on '/api/bringup/start'"
}
```
if navigation is running
```json
{
    "data": {
        "launcher": "NAVIGATION"
    },
    "error": true,
    "message": "first stop navigation on '/api/navigation/stop'"
}
```
 if already mapping is running
 ```json
{
    "data": {
        "launcher": "MAPPING"
    },
    "error": true,
    "message": "mapping is running you should stop current mapping on '/api/mapping/stop'"
}
```
if request body is wrong
```json
{
    "data": {
        "validation error": "error description"
    },
    "error": true,
    "message": "wrong request"
}
```
if slam_method argument is wrong
```json
{
    "data": {
        "slam_methods": "[slam_methods]",
        "launcher": "BRINGUP"
    },
    "error": true,
    "message": "wrong slam method"
}
```
if everything is OK
```json
{
    "data": {
        "launcher": "BRINGUP"
    },
    "error": false,
    "message": null
}
```

### /api/mapping/stop
##### Response
```json
{
    "data": {
        "launcher": "BRINGUP"
    },
    "error": false,
    "message": null
}
```

### /api/mapping/savemap
##### Request body
```json
{
    "map_name": "map_name"
}
```
 ##### Response 
 if everything is OK
 ```json
{
    "data": {
        "launcher": "MAPPING"
    },
    "error": false,
    "message": "map saved in map_path"
}
```
if map with given name exists
 ```json
{
    "data": null,
    "error": false,
    "message": "map with name map_name already exists"
}
```
if request body is wrong
```json
{
    "data": {
        "validation error": "error description"
    },
    "error": true,
    "message": "wrong request"
}
```
if mapping is off
```json
{
    "data": {
        "launcher": "Launcher state"
    },
    "error": true,
    "message": "first launch mapping on '/api/mapping/start"
}
```
### /api/mapping/getmap
##### Request body
```json
{
    "map_name": "map_name"
}
```
##### Response
if everything is OK
- zip file will be received

if map file with given name does n`t exists
```json
{
    "data": {
        "existing_maps": "[existing_maps]"
    },
    "error": true,
    "message": "map_file 'map_name' doesn't exists"
}
```
if request body is wrong
```json
{
    "data": {
        "validation error": "error description"
    },
    "error": true,
    "message": "wrong request"
}
```
### /api/mapping/loadmap
##### Request body
- key: map_file 
- value: filename.zip

##### Response
if everything is OK
```json
{
    "data": null,
    "error": false,
    "message": "map files saved in /map_path"
}
```
if not key 'map_file' in request body
```json
{
    "data": null,
    "error": true,
    "message": "key 'map_file' doesn't exist"
}
```
if mimetype not zip
```json
{
    "data": null,
    "error": true,
    "message": "'map_file' mimetype must be 'application/zip'"
}
```
if value of map_file None
```json
{
    "data": null,
    "error": true,
    "message": "'map_file' empty"
}
```
### /api/mapping/delete
##### Request body
```json
{
    "map_name": "map_name"
}
```
##### Response
if everything is OK
```json
{
    "data": null,
    "error": false,
    "message": "map map_name deleted"
}
```
if map file with given name does n`t exists
```json
{
    "data": {
        "existing_maps": "[existing_maps]"
    },
    "error": true,
    "message": "map_file 'map_name' doesn't exists"
}
```
if request body is wrong
```json
{
    "data": {
        "validation error": "error description"
    },
    "error": true,
    "message": "wrong request"
}
```

### /api/navigation/start
##### Request body
with_virtual_walls is optional by default false
```json
{
    "map_name": "map_name",
    "with_virtual_walls": true
}
```
##### Response
if everything is OK
```json
{
    "data": {
        "launcher": "NAVIGATION"
    },
    "error": false,
    "message": null
}
```
if map file with given name does n`t exists
```json
{
    "data": {
        "existing_maps": "[existing_maps]"
    },
    "error": true,
    "message": "map_file 'map_name' doesn't exists"
}
```
if request body is wrong
```json
{
    "data": {
        "validation error": "error description"
    },
    "error": true,
    "message": "wrong request"
}
```
if launcher is off
```json
{
    "data": {
        "launcher": "OFF"
    },
    "error": true,
    "message": "first launch bringup on '/api/bringup/start'"
}
```
if already navigation is running
```json
{
    "data": {
        "launcher": "NAVIGATION"
    },
    "error": true,
    "message": "first stop current navigation on '/api/navigation/stop'"
}
```
 if already mapping is running
 ```json
{
    "data": {
        "launcher": "MAPPING"
    },
    "error": true,
    "message": "first stop mapping on '/api/mapping/stop'"
}
```
### /api/navigation/stop
##### Response
```json
{
    "data": {
        "launcher": "BRINGUP"
    },
    "error": false,
    "message": null
}
```
### /api/robot/reboot
##### Response
```json
{
    "data": null,
    "error": false,
    "message": "rebooting robot"
}
```
