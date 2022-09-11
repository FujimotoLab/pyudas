import numpy as np

from pyspedas.utilities.time_double import time_double
from pytplot import get_data, store_data, options, clip, ylim, cdf_to_tplot
from ..load import load

def eiscat(
    trange=['2020-2-5', '2020-2-6'],
    site='all',
    datatype='',
	parameter='',
    fproton=False,
    no_update=False,
    downloadonly=False,
    uname=None,
    passwd=None,
	suffix='',
    get_support_data=False,
    varformat=None,
    varnames=[],
    notplot=False,
    time_clip=False,
    version=None,
    ror=True
):

    #===== Set parameters (1) =====#
    file_format = 'cdf'
    remote_data_dir = 'http://pc115.seg20.nipr.ac.jp/www/eiscatdata/cdf/basic/'
    local_path = 'nipr/eiscat/'
    prefix = 'eiscat_'
    file_res = 3600. * 24
    site_list = ['tro_vhf','tro_uhf','esr_32m','esr_42m'] #'kir_uhf','sod_uhf']
    datatype_list = ['']
    parameter_list = ['']
    time_netcdf=''
    #==============================#

    # Check input parameters
    # site
    if isinstance(site, str):
        st_list = site.lower()
        st_list = st_list.split(' ')
    elif isinstance(site, list):
        st_list = []
        for i in range(len(site)):
            st_list.append(site[i].lower())
    if 'all' in st_list:
        st_list = site_list
    st_list = list(set(st_list).intersection(site_list))

    # datatype
    if isinstance(datatype, str):
        dt_list = datatype.lower()
        dt_list = dt_list.split(' ')
    elif isinstance(datatype, list):
        dt_list = []
        for i in range(len(datatype)):
            dt_list.append(datatype[i].lower())
    if 'all' in dt_list:
        dt_list = datatype_list
    dt_list = list(set(dt_list).intersection(datatype_list))

    # parameter
    if isinstance(parameter, str):
        pr_list = parameter.lower()
        pr_list = pr_list.split(' ')
    elif isinstance(parameter, list):
        pr_list = []
        for i in range(len(parameter)):
            pr_list.append(parameter[i].lower())
    if 'all' in pr_list:
        pr_list = parameter_list
    pr_list = list(set(pr_list).intersection(parameter_list))
    
    if notplot:
        loaded_data = {}
    else:
        loaded_data = []

    for st in st_list:
        print(st)		
        if len(st) < 1:
            varname_st = ''
        else:
            varname_st = st
        st_tmp = st.split('_')
        stn = st_tmp[0]
        ant = st_tmp[1]

        for dt in dt_list:
            print(dt)
            if len(dt) < 1:
                varname_st_dt = varname_st
            else:
                varname_st_dt = varname_st+'_'+dt
                
            for pr in pr_list:
                if len(pr) < 1:
                    varname_st_dt_pr = varname_st_dt
                else:
                    varname_st_dt_pr = varname_st_dt+'_'+pr
				
                if len(varname_st_dt_pr) > 0:
                    suffix = '_'+varname_st_dt_pr

				#===== Set parameters (2) =====#
                pathformat = stn+'/'+ant+'/%Y/eiscat_kn_'+stn+'_'+ant+'_%Y%m%d_v??.cdf'
				#==============================#

                loaded_data_temp = load(trange=trange, site=st, datatype=dt, parameter=pr, \
                    pathformat=pathformat, file_res=file_res, remote_path = remote_data_dir, \
                    local_path=local_path, no_update=no_update, downloadonly=downloadonly, \
                    uname=uname, passwd=passwd, prefix=prefix, suffix=suffix, \
                    get_support_data=get_support_data, varformat=varformat, varnames=varnames, \
                    notplot=notplot, time_clip=time_clip, version=version, \
                    file_format=file_format, time_netcdf=time_netcdf)
            
                if notplot:
                    loaded_data.update(loaded_data_temp)
                else:
                    loaded_data += loaded_data_temp
					
                if (len(loaded_data_temp) > 0) and ror:
                    try:
                        if isinstance(loaded_data_temp, list):
                            if downloadonly:
                                cdf_file = cdflib.CDF(loaded_data_temp[-1])
                                gatt = cdf_file.globalattsget()
                            else:
                                gatt = get_data(loaded_data_temp[-1], metadata=True)['CDF']['GATT']
                        elif isinstance(loaded_data_temp, dict):
                            gatt = loaded_data_temp[list(loaded_data_temp.keys())[-1]]['CDF']['GATT']
                        print('**************************************************************************')
                        print(gatt["Logical_source_description"])
                        print('')
                        print(f'Information about {gatt["Station_code"]}')
                        print(f'PI :{gatt["PI_name"]}')
                        print('')
                        print(f'Affiliations: {gatt["PI_affiliation"]}')
                        print('')
                        print('Rules of the Road for NIPR Fluxgate Magnetometer Data:')
                        print('')
                        print(gatt["TEXT"])
                        print(f'{gatt["LINK_TEXT"]} {gatt["HTTP_LINK"]}')
                        print('**************************************************************************')
                    except:
                        print('printing PI info and rules of the road was failed')
                
                if (not downloadonly) and (not notplot):
                    '''
                   REPLACE DATA 
                    
                    #===== Remove tplot variables =====#
                    current_tplot_name = prefix+'epoch'
                    if current_tplot_name in loaded_data:
                        store_data(current_tplot_name, delete=True)
                        loaded_data.remove(current_tplot_name)
'''
                    #===== Rename tplot variables and set options =====#
                    titlehead = stn+'_'+ant+'!C'
                    current_tplot_name = prefix+'pulse_code_id_0_'+st
                    if current_tplot_name in loaded_data:
                        get_data_vars = get_data(current_tplot_name)
                        if get_data_vars is None:
                            store_data(current_tplot_name, delete=True)
                        else:
                            #;--- Rename
                            new_tplot_name = prefix+stn+ant+'_pulse'
                            store_data(current_tplot_name, newname=new_tplot_name)
                            loaded_data.remove(current_tplot_name)
                            loaded_data.append(new_tplot_name)
                            #;--- Missing data -1.e+31 --> NaN
                            clip(new_tplot_name, -1e+5, 1e+5)
                            get_data_vars = get_data(new_tplot_name)
                            ylim(new_tplot_name, np.nanmin(get_data_vars[1]), np.nanmax(get_data_vars[1]))
                            #;--- Labels
                            options(new_tplot_name, 'legend_names', ['Pulse code ID'])
                            #options(new_tplot_name, 'Color', ['b', 'g', 'r'])
                            options(new_tplot_name, 'ytitle', titlehead+'Pulde code ID')
                            #options(new_tplot_name, 'ysubtitle', '[V]')
                            
                    current_tplot_name = prefix+'int_time_nominal_0_'+st
                    if current_tplot_name in loaded_data:
                        get_data_vars = get_data(current_tplot_name)
                        if get_data_vars is None:
                            store_data(current_tplot_name, delete=True)
                        else:
                            #;--- Rename
                            new_tplot_name = prefix+stn+ant+'_inttim'
                            store_data(current_tplot_name, newname=new_tplot_name)
                            loaded_data.remove(current_tplot_name)
                            loaded_data.append(new_tplot_name)
                            #;--- Missing data -1.e+31 --> NaN
                            clip(new_tplot_name, -1e+5, 1e+5)
                            get_data_vars = get_data(new_tplot_name)
                            if np.all(np.isnan(get_data_vars[1])):
                                ylim(new_tplot_name, -50, 350)
                            else:
                                ylim(new_tplot_name, np.nanmin(get_data_vars[1]), np.nanmax(get_data_vars[1]))
                            #;--- Labels
                            options(new_tplot_name, 'legend_names', ['int.time'])
                            #options(new_tplot_name, 'Color', ['b', 'g', 'r'])
                            options(new_tplot_name, 'ytitle', titlehead+'Int. time')
                            options(new_tplot_name, 'ysubtitle', '[s]')             
                    
                    current_tplot_name = prefix+'lat_0_'+st
                    if current_tplot_name in loaded_data:
                        get_data_vars = get_data(current_tplot_name)
                        if get_data_vars is None:
                            store_data(current_tplot_name, delete=True)
                        else:
                            #;--- Rename
                            new_tplot_name = prefix+stn+ant+'_lat'
                            store_data(current_tplot_name, newname=new_tplot_name)
                            store_data(new_tplot_name, new_tplot_name[2]=new_tplot_name[1])
                            loaded_data.remove(current_tplot_name)
                            loaded_data.append(new_tplot_name)
                            #;--- Missing data -1.e+31 --> NaN
                            clip(new_tplot_name, -1e+5, 1e+5)
                            get_data_vars = get_data(new_tplot_name)
                            ylim(current_tplot_name, np.nanmin(get_data_vars[1]), np.nanmax(get_data_vars[1]))
                            #;--- Labels
                            options(new_tplot_name, 'legend_names', ['Lat'])
                            options(new_tplot_name, 'ytitle', titlehead+'Latitude')
                            options(new_tplot_name, 'ysubtitle', 'Latitude [deg]')
                            options(new_tplot_name, 'spec',1)
                            options(new_tplot_name, 'ztitle','Latitude [deg]')

                    current_tplot_name = prefix+'long_0_'+st
                    if current_tplot_name in loaded_data:
                        get_data_vars = get_data(current_tplot_name)
                        if get_data_vars is None:
                            store_data(current_tplot_name, delete=True)
                        else:
                            #;--- Rename
                            new_tplot_name = prefix+stn+ant+'_long'
                            store_data(current_tplot_name, newname=new_tplot_name)
                            loaded_data.remove(current_tplot_name)
                            loaded_data.append(new_tplot_name)
                            #;--- Missing data -1.e+31 --> NaN
                            clip(new_tplot_name, -1e+5, 1e+5)
                            get_data_vars = get_data(new_tplot_name)
                            ylim(new_tplot_name, np.nanmin(get_data_vars[1]), np.nanmax(get_data_vars[1]))
                            #;--- Labels
                            options(new_tplot_name, 'legend_names', ['Lon'])
                            options(new_tplot_name, 'ytitle', titlehead+'Longtitude')
                            options(new_tplot_name, 'ysubtitle', 'Longtitude [deg]')
                            options(new_tplot_name, 'spec',1)
                            options(new_tplot_name, 'ztitle','Longitude [deg]')                            
                    current_tplot_name = prefix+'alt_0_'+st
                    if current_tplot_name in loaded_data:
                        get_data_vars = get_data(current_tplot_name)
                        if get_data_vars is None:
                            store_data(current_tplot_name, delete=True)
                        else:
                            #;--- Rename
                            new_tplot_name = prefix+stn+ant+'_alt'
                            store_data(current_tplot_name, newname=new_tplot_name)
                            loaded_data.remove(current_tplot_name)
                            loaded_data.append(new_tplot_name)
                            #;--- Missing data -1.e+31 --> NaN
                            clip(new_tplot_name, -1e+5, 1e+5)
                            get_data_vars = get_data(new_tplot_name)
                            ylim(new_tplot_name, np.nanmin(get_data_vars[1]), np.nanmax(get_data_vars[1]))
                            #;--- Labels
                            options(new_tplot_name, 'legend_names', ['Alt'])
                            options(new_tplot_name, 'ytitle', titlehead+'Altitude')
                            options(new_tplot_name, 'ysubtitle', 'Altitude [km]')
                            options(new_tplot_name, 'spec',1)
                            options(new_tplot_name, 'ztitle','Altitude [km]')
                            
                    current_tplot_name = prefix+'range_0_'+st
                    if current_tplot_name in loaded_data:
                        get_data_vars = get_data(current_tplot_name)
                        if get_data_vars is None:
                            store_data(current_tplot_name, delete=True)
                        else:
                            #;--- Rename
                            new_tplot_name = prefix+stn+ant+'_range'
                            store_data(current_tplot_name, newname=new_tplot_name)
                            loaded_data.remove(current_tplot_name)
                            loaded_data.append(new_tplot_name)
                            #;--- Missing data -1.e+31 --> NaN
                            clip(new_tplot_name, -1e+5, 1e+5)
                            get_data_vars = get_data(new_tplot_name)
                            ylim(new_tplot_name, np.nanmin(get_data_vars[1]), np.nanmax(get_data_vars[1]))
                            #;--- Labels
                            options(new_tplot_name, 'legend_names', ['Range'])
                            options(new_tplot_name, 'ytitle', titlehead+'Range')
                            options(new_tplot_name, 'ysubtitle', '????')
                            options(new_tplot_name, 'spec', 1)
                            options(new_tplot_name, 'ztitle',' Range [km]')                            
                            
    return loaded_data
