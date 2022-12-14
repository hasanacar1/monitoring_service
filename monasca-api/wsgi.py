# Copyright 2017 FUJITSU LIMITED
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# extremely simple way to setup of monasca-api
# with wsgi

import server


def main():
    #return server.get_wsgi_app(config_base_path='monasca-api/api_conf/')
    return server.get_wsgi_app()

if __name__ == '__main__' or __name__.startswith('_mod_wsgi'):
    application = main()
