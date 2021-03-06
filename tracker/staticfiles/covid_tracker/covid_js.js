


function addFiltersToUri(uri, filters) {
  var finalUri = uri;
  var filterSuffixUri = '';
  var first = true;
  for (var key in filters) {
    if (filters.hasOwnProperty(key)) {
      if (first) {
        filterSuffixUri = key + '=' + filters[key];
        first = false;
      } else {
        filterSuffixUri = filterSuffixUri + '&' + key + '=' + filters[key];
      }
    }
  }
  finalUri = finalUri + '?' + filterSuffixUri;
  return finalUri;
}

function updateChart(divId, uri, filters) {

  let divIdWithHash = '#' + divId;
  var chart_div = document.querySelector(divIdWithHash);
  var finalUri = addFiltersToUri(uri, filters)

  // show pre-loading
  // chart_div.innerHTML = "<img style=\"height:400px\" src={% static 'covid_tracker/assets/pre-loader-1.gif' %}>";
  chart_div.innerHTML = "<img style='height:100px' src='" + static_path + "/assets/pre-loader-4.gif'>";
  // chart_div.innerHTML = "<iframe src=\"https://giphy.com/embed/dUf4MkUk6GpuMDrNbj\" width=\"100%\" height=\"100%\" style=\"position:absolute\" frameBorder=\"0\" class=\"giphy-embed\" allowFullScreen></iframe>"


  fetch(finalUri)
            .then(function (response) {
                return response.json();
            })
            .then(function (item) {
                var chart_div = document.querySelector(divIdWithHash);
                chart_div.innerHTML = "";
                Bokeh.embed.embed_item(item, divId);
                chart_div.setAttribute('data-url', finalUri);
            }).catch((error) => {
                var chart_div = document.querySelector(divIdWithHash);
                chart_div.innerHTML = "<img src='" + static_path + "/assets/tech-snag.png'>";
                chart_div.setAttribute('data-url', finalUri);
            });

}

function determine_filters(data_group_class) {
  var elem_list = document.getElementsByClassName(data_group_class);
  var filters = {};
  for (let i = 0; i < elem_list.length; i++) {
    filters[elem_list[i].dataset.key] = elem_list[i].dataset.value.toLowerCase();
  }

  return filters;
}

function determine_and_update(chartId, data_group_class, uri) {
  var updates_filters = determine_filters(data_group_class);
  console.log(updates_filters)
  updateChart(chartId, uri, updates_filters);
}


function update_counties(state, county_id, data_group_class, target_chart, chart_update_url, chart_name) {
  // when a new state is selected, this function will update
  // the counties dropdown list.
  var county_sel = document.getElementById(county_id).getElementsByClassName('dropdown-menu')[0];
  var data_div = document.getElementById(county_id).getElementsByClassName(data_group_class)[0];
  var btn = document.getElementById(county_id).getElementsByClassName('btn')[0]

  btn.disabled = true;
  var btn_span = document.createElement('span');
  btn_span.className = "spinner-border spinner-border-sm text-light";
  btn_span.role = 'status';
  btn.appendChild(btn_span);
  btn.innerText = 'loading...';

  // clear the exiting list
  while (county_sel.firstChild) {
    county_sel.removeChild(county_sel.firstChild);
  }

  const counties_list = states_dict[state];

  var opt;
  for (var county in counties_list) {
    opt = document.createElement('a');
    opt.className = 'dropdown-item';
    opt.href = '#' + chart_name;
    opt.innerText = counties_list[county];
    opt.onclick = (x) => {
      btn.innerText = x.target.text;
      btn.setAttribute('data-value', x.target.text);
      determine_and_update(target_chart, data_group_class, chart_update_url);
    }
    county_sel.appendChild(opt);
    if (counties_list[county] === 'All') {
      var divider = document.createElement('div');
      divider.className="dropdown-divider";
      county_sel.appendChild(divider);
    }

  }
  data_div.innerText = 'All';
  data_div.setAttribute('data-value', 'All');
  btn.disabled = false;
}

function make_county_dropdown(data_group_class, add_to_div, target_chart, chart_update_url, button_label, chart_name) {
  make_button_dropdown(data_group_class, add_to_div, target_chart, chart_update_url, {'county': ['All']}, button_label, chart_name)
}

function make_exclcounty_dropdown(data_group_class, add_to_div, target_chart, chart_update_url, button_label, chart_name) {
  make_multibutton_dropdown(data_group_class, add_to_div, target_chart, chart_update_url, {'county': ['All']}, button_label, chart_name)
}

function make_state_dropdown(data_group_class, add_to_div, target_chart, chart_update_url, button_label, chart_name, default_value) {
  // const states_wo_totalUS = states_list.slice(1, states_list.length);
  make_button_dropdown(data_group_class, add_to_div, target_chart, chart_update_url, {'state': states_list}, button_label, chart_name, default_value);
}

function make_statewoUS_dropdown(data_group_class, add_to_div, target_chart, chart_update_url, button_label, chart_name, default_value) {
  const states_wo_totalUS = states_list.slice(1, states_list.length);
  make_button_dropdown(data_group_class, add_to_div, target_chart, chart_update_url, {'state': states_wo_totalUS}, button_label, chart_name, default_value);
}

function make_slider(data_group_class, add_to_div, target_chart, chart_update_url, key_value_name, slider_title, values_dict, chart_name) {
  // values_dict = {'min': , 'max':, 'value': }
  var slider_div = document.createElement('div');
  slider_div.className = 'my-3';

  var slider_id = data_group_class + '_slider';
  var slider_label = document.createElement('label');
  slider_label.for = slider_id;
  slider_label.innerText = slider_title;
  var slider_span = document.createElement('span');
  slider_span.id = slider_id + '_days';
  slider_span.innerText = values_dict['value'].toString();
  slider_label.appendChild(slider_span);
  var slider_input = document.createElement('input');
  slider_input.type = 'range';
  slider_input.min = values_dict['min'];
  slider_input.max = values_dict['max'];
  slider_input.value = values_dict['value'];
  slider_input.id = slider_id;
  slider_input.className = 'slider ' + data_group_class;
  slider_input.setAttribute('data-key', key_value_name);
  slider_input.setAttribute('data-value', slider_input.value);
  slider_input.oninput = x => {
                                slider_span.innerText = x.target.value;
                              };
  slider_input.onchange = x => {
                            slider_span.innerText = x.target.value;
                            slider_input.setAttribute('data-value', slider_input.value);
                            determine_and_update(target_chart, data_group_class, chart_update_url);
                          };

  // build new slider div and append to page
  slider_div.appendChild(slider_label);
  slider_div.appendChild(slider_input);
  document.getElementById(add_to_div).appendChild(slider_div);

}

function make_button_dropdown(data_group_class, add_to_div, target_chart, chart_update_url, sel_options, button_label, chart_name, default_value) {

  var key = Object.keys(sel_options)[0];
  var options = sel_options[key];

  // if no default_value is provided, select the first item in the options list
  if (!default_value) {
    default_value = options[0];
  }

  var row_div = document.createElement('div');
  row_div.className = 'row';
  row_div.style = 'display: block';
  var dropdown_div = document.createElement('div');
  row_div.appendChild(dropdown_div)
  dropdown_div.className = 'btn-group dropright'; // 'btn-group' 'dropdown show'
  dropdown_div.style = 'display: block';

  var new_label = document.createElement('label');
  new_label.innerText = button_label;
  dropdown_div.appendChild(new_label)

  var new_btn = document.createElement('div');
  new_btn.className = 'btn btn-sm btn-custom btn-block dropdown-toggle ' + data_group_class;
  new_btn.href = '#';
  new_btn.role = 'button';
  new_btn.setAttribute('data-toggle', 'dropdown');
  new_btn.setAttribute('data-key', key);
  new_btn.setAttribute('data-value', default_value);
  new_btn.setAttribute('aria-haspopup', 'true');
  new_btn.setAttribute('aria-expanded', 'false');
  new_btn.innerText = default_value;
  dropdown_div.appendChild(new_btn);

  var new_menu = document.createElement('div');
  new_menu.className = 'dropdown-menu';
  new_menu.setAttribute('style', 'overflow-y:scroll; max-height:50vh');
  new_menu.setAttribute('aria-labelledby', 'dropdownMenuLink');
  dropdown_div.appendChild(new_menu);

  var elem;
  for (var i in options) {
    elem = document.createElement('a');
    elem.className = 'dropdown-item';
    elem.href = '#' + chart_name;
    elem.innerText = options[i];
    elem.onclick = (x) => {
                            var county_id = document.getElementById(add_to_div).dataset.county_id;
                            if (county_id) {
                              document.getElementById(county_id).getElementsByClassName(data_group_class)[0].setAttribute('data-value', 'All');
                              document.getElementById(county_id).getElementsByClassName(data_group_class)[0].innerText = 'All';
                              update_counties(x.target.text, county_id, data_group_class, target_chart, chart_update_url, chart_name);
                            }
                            new_btn.innerText = x.target.text;
                            new_btn.setAttribute('data-value', x.target.text);
                            determine_and_update(target_chart, data_group_class, chart_update_url);
                          }
    new_menu.appendChild(elem);

    // Add a drop down listing divider if item is 'United States' or 'All
    if (options[i] === 'All' | options[i] === 'United States') {
      var divider = document.createElement('div');
      divider.className="dropdown-divider";
      new_menu.appendChild(divider);
    }
  }
  document.getElementById(add_to_div).appendChild(row_div);
}

function make_multibutton_dropdown(data_group_class, add_to_div, target_chart, chart_update_url, sel_options, button_label, chart_name) {
  var key = Object.keys(sel_options)[0];
  var options = sel_options[key];

  var row_div = document.createElement('div');
  row_div.className = 'row';
  row_div.style = 'display: block';
  var dropdown_div = document.createElement('div');
  row_div.appendChild(dropdown_div)
  dropdown_div.className = 'dropdown show';
  dropdown_div.style = 'display: block';

  var new_label = document.createElement('label');
  new_label.innerText = button_label;
  dropdown_div.appendChild(new_label)

  var new_btn = document.createElement('div');
  new_btn.className = 'btn btn-sm btn-success btn-block dropdown-toggle ' + data_group_class;
  new_btn.href = '#';
  new_btn.role = 'button';
  new_btn.setAttribute('data-toggle', 'dropdown');
  new_btn.setAttribute('data-key', key);
  new_btn.setAttribute('data-value', options[0]);
  new_btn.setAttribute('aria-haspopup', 'true');
  new_btn.setAttribute('aria-expanded', 'false');
  new_btn.innerText = options[0];
  dropdown_div.appendChild(new_btn);

  var new_menu = document.createElement('div');
  new_menu.className = 'dropdown-menu';
  new_menu.setAttribute('aria-labelledby', 'dropdownMenuLink');
  dropdown_div.appendChild(new_menu);

  var elem;
  for (var i in options) {
    elem = document.createElement('a');
    elem.className = 'dropdown-item';
    elem.href = '#' + chart_name;
    elem.innerText = options[i];
    elem.onclick = (x) => {
                            // var county_id = document.getElementById(add_to_div).dataset.county_id;
                            // if (county_id) {
                            //   document.getElementById(county_id).getElementsByClassName(data_group_class)[0].setAttribute('data-value', 'All');
                            //   document.getElementById(county_id).getElementsByClassName(data_group_class)[0].innerText = 'All';
                            //   update_counties(x.target.text, county_id, data_group_class, target_chart, chart_update_url);
                            // }
                            // new_btn.innerText = x.target.text;
                            // new_btn.setAttribute('data-value', x.target.text);
                            // determine_and_update(target_chart, data_group_class, chart_update_url);
                          }
    new_menu.appendChild(elem);
  }
  document.getElementById(add_to_div).appendChild(row_div);
}

function make_info_modal(infodiv_to_show, add_to_div, button_label) {

  var target_modal_id = add_to_div + '_info';

  var row_div = document.createElement('div');
  row_div.className = 'row mt-5';
  row_div.style = 'display: block';

  var launch_button = document.createElement('button');
  launch_button.type = 'button';
  launch_button.className = "btn btn-light btn-sm btn-block";
  launch_button.setAttribute('data-toggle', 'modal');
  launch_button.setAttribute('data-target', '#' + target_modal_id)
  launch_button.innerText = button_label;
  launch_button.style = 'display: block';
  row_div.appendChild(launch_button);

  var modal_top_level = document.createElement('div');
  modal_top_level.className = 'modal fade';
  modal_top_level.id = target_modal_id;
  modal_top_level.tabIndex = -1;
  modal_top_level.setAttribute('role', 'dialog');
  row_div.appendChild(modal_top_level);

  var modal_dialog = document.createElement('div');
  modal_dialog.className = 'modal-dialog';
  modal_dialog.setAttribute('role', 'document');
  modal_top_level.appendChild(modal_dialog);

  var modal_content = document.createElement('div');
  modal_content.className = 'modal-content';
  modal_dialog.appendChild(modal_content);

  var modal_header = document.createElement('div');
  modal_header.className = 'modal-header';
  modal_content.appendChild(modal_header);

  var modal_title = document.createElement('h5');
  modal_title.className = 'modal_title';
  modal_title.id = 'target_modal_label';
  modal_title.innerText = "Political Affiliation of States (based on governors' affiliation)";
  modal_header.appendChild(modal_title);

  var dismiss_button_x = document.createElement('button');
  dismiss_button_x.type = 'button';
  dismiss_button_x.className = 'close';
  dismiss_button_x.setAttribute('data-dismiss', 'modal');
  var dismiss_x = document.createElement('span');
  dismiss_x.innerHTML = '<span>&times;</span>';
  dismiss_button_x.appendChild(dismiss_x);
  modal_header.appendChild(dismiss_button_x);

  var modal_body = document.createElement('div');
  modal_body.className = 'modal-body';
  modal_content.appendChild(modal_body);

  var modal_body_p = document.createElement('p');
  modal_body_p.innerHTML = infodiv_to_show.innerHTML;
  modal_body.appendChild(modal_body_p);

  document.getElementById(add_to_div).appendChild(row_div);

}

function make_chart(default_filters, chart_name, chart_title, chart_update_url){
  // default_filters: {'key': value}
  // A series of k/v pairs where each key drives the control elements for a plot.
  // The keys should match the variables accepted by the python view function
  // which creates the plot.  Values are the defaults.
  // The following keys are supported:
  //  state -  creates a state drop down with the 'United States' as the first element
  //  state_wo_us - creates a state drop down without the 'Unites States'
  //  county - creates a County listing dropdown which is updated by the state
  //          A county dropdown is only created if a state of state_wo_us k/v is available.
  //          The county listing will be tied to that counties of the selected state.
  //          The default value for county is ignored and 'All' is used as the default.
  //  FUTURE exclude_counties - creates a dropdown that will exclude counties from the plot
  //  FUTURE exclude_states - creates a dropdown that will exclude states from the plot
  //  rolling_window - creates a slider that is used to adjust the # of days used in avg daily value line in plot
  //  top_n_counties - creates a slider that will include the top counties in a plot
  //  top_n_states - creates a slider that will include the top states in a plot
  //  frequency - creates a drop down button that accepts 'daily' or 'cumulative' input from the user
  //  data_type - creates a drop down button that accepts 'deaths' of 'infections' from the user

  // the data_group_name is used to find elements of a plot that contain data values
  // which are used to update the plot.
  const data_group_name = chart_name + '_data_group';

  // create separate divs for control elements and the plot
  var section_div = document.createElement('div');
  section_div.className = 'container m-3';
  section_div.id = chart_name;

  // add a space for the navbar
  var section_spacer = document.createElement('div');
  // section_spacer.setAttribute('style', 'height=50px');
  section_spacer.style.height = '70px';
  section_div.appendChild(section_spacer);

  // add chart to the navbar
  var navbar_list = document.getElementById("navbar_list");
  var new_navelement = document.createElement('li');
  new_navelement.className = 'nav-item';
  var new_navelement_link = document.createElement('a')
  new_navelement_link.className = 'nav-link';
  new_navelement_link.href = '#' + chart_name;
  new_navelement_link.innerText = chart_title;

  new_navelement.appendChild(new_navelement_link);
  navbar_list.appendChild(new_navelement);

  var title = document.createElement('h3');
  title.className = 'row p-2 title-custom';
  // title.style = 'background-color: darkseagreen';
  title.innerText = chart_title;
  section_div.appendChild(title);

  var content_div = document.createElement('div');
  content_div.className = 'row';
  content_div.style.height = "500px";
  content_div.style.width = "900px";
  section_div.appendChild(content_div);

  var controls_div = document.createElement('div');
  controls_div.className = 'col-2 mt-2';
  controls_div.id = chart_name + '_controls';
  content_div.appendChild(controls_div);

  var chart_div = document.createElement('div');
  chart_div.className = 'col-9 mx-auto my-auto';
  chart_div.id = chart_name + '_chart';
  content_div.appendChild(chart_div);

  document.getElementById('chart-section').appendChild(section_div);

  // make a region section with a state if 'state' or 'state_wo_us' exists
  if (default_filters.hasOwnProperty('state') | default_filters.hasOwnProperty('state_wo_us')) {
    var region_div = document.createElement('div');
    region_div.id = controls_div.id + '_regions';
    region_div.className = 'mb-3';
    controls_div.appendChild(region_div);

    var state_div = document.createElement('div');
    state_div.id = region_div.id + '_state';
    region_div.appendChild(state_div);

    if (default_filters.hasOwnProperty('state')) {
      make_state_dropdown(data_group_name, state_div.id, chart_div.id, chart_update_url, 'State: ', chart_name, default_filters['state']);
    }

    if (default_filters.hasOwnProperty('state_wo_us')) {
      make_statewoUS_dropdown(data_group_name, state_div.id, chart_div.id, chart_update_url, 'State: ', chart_name, default_filters['state_wo_us']);
    }

    // make a county section if 'county' exists - tie it to the selected state
    if (default_filters.hasOwnProperty('county')) {
      var county_div = document.createElement('div');
      region_div.appendChild(county_div);
      county_div.id = region_div.id + '_county';
      state_div.setAttribute('data-county_id', county_div.id);

      make_county_dropdown(data_group_name, county_div.id, chart_div.id, chart_update_url, 'County: ', chart_name);
    }
  }

  // FUTURE make an exclude county section is 'exclude_counties' exists - tie it to state
  // if (default_filters.hasOwnProperty('exclude_counties')){
  //   var excl_county_div = document.createElement('div');
  //   region_div.appendChild(excl_county_div);
  //   excl_county_div.id = region_div.id + '_exclcounties';
  //   state_div.setAttribute('data-exclcounties_id', excl_county_div.id);
  //
  //   make_exclcounty_dropdown(data_group_name, excl_county_div.id, chart_div.id, chart_update_url, 'Exclude Counties: ', chart_name);
  // }

  // make slider if 'rolling_window' exists
  if (default_filters.hasOwnProperty('rolling_window')){
    make_slider(data_group_name, controls_div.id, chart_div.id, chart_update_url, 'rolling_window', 'Rolling Avg Days: ', {'min': 1, 'max': 21, 'value': default_filters['rolling_window']}, chart_name);
  }

  // make slider if 'top_n_counties' exists
  if (default_filters.hasOwnProperty('top_n_counties')){
    make_slider(data_group_name, controls_div.id, chart_div.id, chart_update_url, 'top_n_counties', 'Top n Counties: ', {'min': 1, 'max': 15, 'value': default_filters['top_n_counties']}, chart_name);
  }

  // make slider if 'top_n_counties' exists
  if (default_filters.hasOwnProperty('top_n_states')){
    make_slider(data_group_name, controls_div.id, chart_div.id, chart_update_url, 'top_n_states', 'Top n States: ', {'min': 1, 'max': 15, 'value': default_filters['top_n_states']}, chart_name);
  }

  // make frequency button if 'frequency' exists
  if (default_filters.hasOwnProperty('frequency')) {
    make_button_dropdown(data_group_name, controls_div.id, chart_div.id, chart_update_url, {'frequency': ['Daily', 'Cumulative']}, 'Frequency: ', chart_name);
  }

  // make data_type button if 'data_type' exists
  if (default_filters.hasOwnProperty('data_type')) {
    make_button_dropdown(data_group_name, controls_div.id, chart_div.id, chart_update_url, {'data_type': ['Infections', 'Deaths']}, 'Data Type: ', chart_name);
  }

  updateChart(chart_div.id, chart_update_url, default_filters);

}

function add_footer() {
  var footer = document.createElement('div');
  footer.innerHTML = "<span style='color: black'>Data Source:&nbsp;<span><span style='color: antiquewhite'>COVID-19 Data Repository by the Center for Systems Science and Engineering (CSSE) at Johns Hopkins University&nbsp;</span><a href='https://github.com/CSSEGISandData/COVID-19' target='_blank'>(source)</a>";

  document.getElementById('footer-section').appendChild(footer);

}

function draw_covid_tracker() {
  fetch('/refresh_git')
    .then(response => console.log(response.json()))
    .then(() => {
      // infections by state
      var filters = {
        'state': 'United States',
        'county': 'All',
        'frequency': 'daily',
        'data_type': 'Infections',
        'rolling_window': 14
      };
      make_chart(filters, 'state_totals', 'State Totals', '/state_chart/');
    })
    .then(() => {
      // infections by county
      var filters = {
        'state_wo_us': 'Massachusetts',
        // 'exclude_counties': null,
        'top_n_counties': 10,
        'data_type': 'Infections'
      }
      make_chart(filters, 'state_by_county', 'Counties by State', '/state_by_county_chart/');

    })
    .then(() => {
      // numbers by political affiliation of states
      var filters = { 'frequency': 'daily',
                      'data_type': 'infections',
                      'rolling_window': 14,
                      // 'exclude_states': null
                    }
      make_chart(filters, 'political_affiliation', 'Political Affiliation', '/political_affiliation/');
      // make a div with affiliation mappings
      var affil_div = document.createElement('div');
      var affil_table = document.createElement('table');
      affil_table.className = 'table';
      affil_div.appendChild(affil_table);

      var affil_table_head = document.createElement('thead');
      affil_table_head.className = "thead-dark";
      affil_table.appendChild(affil_table_head);

      var affil_table_head_rows = document.createElement('tr');
      affil_table_head.appendChild(affil_table_head_rows);

      var col1 = document.createElement('th');
      col1.innerText = "Region";
      affil_table_head_rows.appendChild(col1)

      var col2 = document.createElement('th');
      col2.innerText = "Affiliation";
      affil_table_head_rows.appendChild(col2)

      var table_body = document.createElement('tbody');
      affil_table.appendChild(table_body)

      for (var trow_state in political_affiliation_map) {

        if (political_affiliation_map.hasOwnProperty(trow_state) && political_affiliation_map[trow_state]!=='na') {
          var trow = document.createElement('tr');
          trow.setAttribute('style', 'line-height: 10px')

          var trow_head = document.createElement('th');
          trow_head.scope = 'row';
          trow_head.innerText = trow_state;

          var trow_data = document.createElement('td');
          trow_data.innerText = political_affiliation_map[trow_state];

          trow.appendChild(trow_head);
          trow.appendChild(trow_data);
          table_body.appendChild(trow);
        }
      }

      make_info_modal(affil_div, "political_affiliation_controls", "Affiliation Info")
    })
    .then(() => {
      // numbers by top states
      var filters = { 'states': null,
                      'data_type': 'infections',
                      'top_n_states': 10,
                      // 'exclude_states': null
                    }
      make_chart(filters, 'top_states', 'Top States', '/top_states/');
    })
    .then(() => add_footer())
    .catch( error => console.log(error))
}