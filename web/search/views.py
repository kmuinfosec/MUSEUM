from django.shortcuts import render, redirect
from django.template import loader
from django.http import HttpResponse, HttpResponseBadRequest
from pathlib import Path
from urllib import parse
import json
import urllib.request
import urllib.error

from museum import api


def connect_view(request):
    template = loader.get_template('search/connect.html')
    context = {}
    return HttpResponse(template.render(context, request))


def indices_view(request):
    if request.method == "POST":
        if 'es-host' not in request.POST:
            return redirect('search:connect')
        es_host = request.POST['es-host']

        try:
            es_content = json.dumps(urllib.request.urlopen(es_host).read().decode('utf-8'))
        except urllib.error.URLError:
            return redirect('search:connect')
        except json.decoder.JSONDecodeError:
            return redirect('search:connect')
        if 'name' not in es_content or 'version' not in es_content or 'tagline' not in es_content:
            return redirect('search:connect')

        request.session['es-host'] = es_host

    es_host = request.session.get('es-host', False)
    if not es_host:
        return redirect('search:connect')

    indices = api.cat_indices(es_host)

    template = loader.get_template('search/indices.html')
    context = {
        'es_host': es_host,
        'indices': indices
    }
    return HttpResponse(template.render(context, request))


def create_index_view(request):
    es_host = request.session.get('es-host', False)
    if not es_host:
        return redirect('search:connect')

    if request.method == "POST" and 'form_data' in request.POST:
        form_data = parse.unquote(request.POST['form_data'])
        form_dict = {'use_minmax': False}
        for attribute in form_data.split('&'):
            if attribute.startswith('module_params='):
                module_param_dict = {}
                for param in attribute.replace('module_params=', '').split(','):
                    param = param.strip()
                    if '=' not in param:
                        continue
                    k, v = param.split('=')
                    if not k or not v:
                        continue
                    module_param_dict[k] = eval(v)
                form_dict['module_params'] = module_param_dict
            else:
                k, v = attribute.split('=')
                if not v:
                    return HttpResponseBadRequest('Empty value detected')

                if k != 'index_name' and k != 'module_name':
                    v = eval(v.strip())
                    if type(v) is int and v < 1:
                        return HttpResponseBadRequest('Invalid value detected')

                form_dict[k] = v

        is_created = api.create_index(es_host, form_dict['index_name'], form_dict['module_name'],
                                      form_dict['module_params'], form_dict['num_hash'], form_dict['use_smallest'],
                                      form_dict['use_minmax'], False, form_dict['intervals'], form_dict['shards'],
                                      form_dict['replicas'])

        if is_created:
            response = HttpResponse(json.dumps({'status': '200'}), content_type='application/json')
            response.status_code = 200
            return response
        else:
            return HttpResponseBadRequest('Fail to create index')

    else:
        response = HttpResponse()
        response.status_code = 400
        return response


def index_info_view(request, index_name):
    es_host = request.session.get('es-host', False)
    if not es_host:
        return redirect('search:connect')

    index_info = api.get_index_info(es_host, index_name)
    template = loader.get_template('search/index_info.html')
    context = {'index_info': index_info}
    return HttpResponse(template.render(context, request))


def index_delete_view(request, index_name):
    es_host = request.session.get('es-host', False)
    if not es_host:
        return redirect('search:connect')

    api.delete_index(es_host, index_name)
    return redirect('search:indices')


def index_bulk_view(request, index_name):
    es_host = request.session.get('es-host', False)
    if not es_host:
        return redirect('search:connect')

    index_info = api.get_index_info(es_host, index_name)

    if request.method == "POST":
        if 'dir_path' not in request.POST:
            return HttpResponseBadRequest('Invalid request')

        dir_path = request.POST['dir_path'].strip('"').strip()
        if not dir_path or not Path(dir_path).is_dir():
            return HttpResponseBadRequest('Invalid request')

        dir_path = Path(dir_path)
        api.bulk(es_host, index_name, dir_path, process=1, disable_tqdm=True)

        response = HttpResponse(json.dumps({'status': '200', 'reason': ''}), content_type='application/json')
        response.status_code = 200
        return HttpResponse(response)

    else:
        template = loader.get_template('search/index_bulk.html')
        context = {'index_info': index_info}
        return HttpResponse(template.render(context, request))


def index_msearch_view(request, index_name):
    es_host = request.session.get('es-host', False)
    if not es_host:
        return redirect('search:connect')

    index_info = api.get_index_info(es_host, index_name)

    if request.method == "POST":
        if 'dir_path' not in request.POST:
            return HttpResponseBadRequest('Invalid request')

        dir_path = request.POST['dir_path'].strip('"').strip()
        if not dir_path or not Path(dir_path).is_dir():
            return HttpResponseBadRequest('Invalid request')

        dir_path = Path(dir_path)
        reports = []
        for _reports in api.msearch(es_host, index_info['index_name'], dir_path, process=1, disable_tqdm=True):
            reports += _reports
        response = HttpResponse(json.dumps({'status': '200', 'reason': '', 'reports': reports}), content_type='application/json')
        response.status_code = 200
        return HttpResponse(response)

    else:
        template = loader.get_template('search/index_msearch.html')
        context = {'index_info': index_info}
        return HttpResponse(template.render(context, request))


def index_search_view(request, index_name):
    es_host = request.session.get('es-host', False)
    if not es_host:
        return redirect('search:connect')

    index_info = api.get_index_info(es_host, index_name)

    if request.method == "POST":
        if 'file_path' not in request.POST:
            return HttpResponseBadRequest('Invalid request')

        file_path = request.POST['file_path'].strip('"').strip()
        if not file_path or not Path(file_path).is_file():
            return HttpResponseBadRequest('Invalid request')

        file_path = Path(file_path)
        report = api.search(es_host, index_info['index_name'], file_path)
        response = HttpResponse(json.dumps({'status': '200', 'reason': '', 'report': report}), content_type='application/json')
        response.status_code = 200
        return HttpResponse(response)

    else:
        template = loader.get_template('search/index_search.html')
        context = {'index_info': index_info}
        return HttpResponse(template.render(context, request))
