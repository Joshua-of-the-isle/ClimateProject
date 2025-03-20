import streamlit as st
import pickle
import heapq
from math import radians, sin, cos, sqrt, atan2
import plotly.graph_objects as go
import pandas as pd

# Load the graph
@st.cache_resource
def load_graph():
    with open(r'C:\Users\joshd\Documents\Programming\IIT-B\graph_final_8_precalc.pkl', "rb") as G:
        return pickle.load(G)

roadsn = load_graph()

# CO2 emission factors (g per ton-km)
#CO2 emission factors
EMISSION_FACTORS = {
    "sea": 0.01,  # 10g per ton-km
    "land": 0.1,  # 100g per ton-km
    "air": 0.7,   # 700g per ton-km
}

waiting_times = {
    "CN": 117.7,
    "AU": 187.1,
    "US": 118.2,
    "BR": 366.3,
    "RU": 106.8,
    "CA": 126.5,
    "AR": 55.7,
    "ZA": 237.5,
    "JP": 68.4,
    "IN": 90.0,
    "UA": 58.8,
    "AE": 79.2,
    "ID": 63.4,
    "KR": 74.7,
    "NZ": 64.8,
    "CL": 280.3,
    "TR": 130.1,
    "VN": 48.6,
    "CO": 83.4,
    "MY": 126.5,
    "MX": 109.2,
    "TW": 71.3,
    "PE": 196.5,
    "OM": 85.4,
    "NO": 45.2,
    "FR": 58.4,
    "SA": 89.5,
    "MA": 227.4,
    "RO": 83.5,
    "MZ": 265.3
}


# Constants
time_min, time_max = 0, 740.8010060257351
price_min, price_max = 0, 49341.63950694249

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def precompute_heuristics(multigraph, goal, time_weight, price_weight):
    goal_pos = multigraph.nodes[goal]
    heuristic_dict = {}
    for node in multigraph.nodes():
        if node == goal:
            heuristic_dict[node] = 0
            continue
        node_pos = multigraph.nodes[node]
        dist = haversine(node_pos['latitude'], node_pos['longitude'], 
                         goal_pos['latitude'], goal_pos['longitude'])
        time_est = dist / 800  # Fastest mode (air)
        price_est = dist * 0.00002  # Cheapest mode (sea)
        time_norm = (time_est - time_min) / (time_max - time_min) * 1000
        price_norm = (price_est - price_min) / (price_max - price_min) * 1000
        heuristic_dict[node] = time_weight * time_norm + price_weight * price_norm
    return heuristic_dict

def astar_top_n_avoid_countries(multigraph, start, goal, avoid_countries=None, 
                              top_n=3, time_weight=0.333, price_weight=0.333, 
                              emissions_weight=0.334, allowed_modes=['land', 'sea', 'air'], 
                              weight=30000):
    if start not in multigraph or goal not in multigraph:
        return {"error": "Start or goal node not in graph"}
    
    avoid_countries = set(avoid_countries) if avoid_countries else set()
    if (multigraph.nodes[start].get('country_code') in avoid_countries or 
        multigraph.nodes[goal].get('country_code') in avoid_countries):
        return {"error": f"No valid route: Start ({start}) or goal ({goal}) is in a banned country."}
    
    # Retrieve precomputed values from graph
    time_min = multigraph.graph['time_min']
    time_max = multigraph.graph['time_max']
    price_min = multigraph.graph['price_min']
    price_max = multigraph.graph['price_max']
    emissions_min = multigraph.graph['emissions_min']
    emissions_max = multigraph.graph['emissions_max']
    max_speed = multigraph.graph['max_speed']
    min_price_per_km = multigraph.graph['min_price_per_km']

    # Compute parameters based on allowed modes
    allowed_modes_set = set(allowed_modes)
    max_speed_allowed = max(max_speed[mode] for mode in allowed_modes_set if mode in max_speed)
    min_price_per_km_allowed = min(min_price_per_km[mode] for mode in allowed_modes_set if mode in min_price_per_km)
    min_emission_factor = min(EMISSION_FACTORS[mode] for mode in allowed_modes_set)

    # Precompute heuristic
    goal_pos = multigraph.nodes[goal]
    heuristic_dict = {}
    for node in multigraph.nodes():
        if node == goal:
            heuristic_dict[node] = 0
            continue
        node_pos = multigraph.nodes[node]
        dist = haversine(node_pos['latitude'], node_pos['longitude'], 
                         goal_pos['latitude'], goal_pos['longitude'])
        if dist == 0:
            heuristic_dict[node] = 0
        else:
            time_est = dist / max_speed_allowed if max_speed_allowed > 0 else float('inf')
            price_est = dist * min_price_per_km_allowed
            emissions_est = dist * min_emission_factor  # g per ton
            time_norm_est = (time_est - time_min) / (time_max - time_min) * 100 if time_max > time_min else 0
            price_norm_est = (price_est - price_min) / (price_max - price_min) * 100 if price_max > price_min else 0
            emissions_norm_est = (emissions_est - emissions_min) / (emissions_max - emissions_min) * 100 if emissions_max > emissions_min else 0
            heuristic_dict[node] = (time_weight * time_norm_est + 
                                   price_weight * price_norm_est + 
                                   emissions_weight * emissions_norm_est)

    queue = [(0, 0, 0, start, [start], [], 0)]
    visited = set()
    counter = 0
    completed_paths = []
    
    while queue:
        f_cost, g_cost, _, current, path, edge_details, total_wait_time = heapq.heappop(queue)
        if current == goal:
            completed_paths.append((path, edge_details, g_cost, total_wait_time))
            if len(completed_paths) >= top_n:
                completed_paths.sort(key=lambda x: x[2])
                if f_cost > completed_paths[top_n-1][2]:
                    break
            continue
        
        if current in visited:
            continue
        visited.add(current)
        
        for u, neighbor, key, data in multigraph.edges(current, keys=True, data=True):
            if data['mode'] not in allowed_modes:
                continue
            neighbor_country = multigraph.nodes[neighbor].get('country_code', '')
            current_country = multigraph.nodes[current].get('country_code', '')
            if neighbor in path or neighbor_country in avoid_countries:
                continue
         
            border_penalty = 1 if current_country != neighbor_country else 0
            mode_waiting_time = 0
            if data['mode'] == 'sea':
                mode_waiting_time = waiting_times.get(neighbor_country, 89.5) / 2
            elif data['mode'] == 'air':
                mode_waiting_time = 2
            
            new_wait_time = total_wait_time + mode_waiting_time
            new_g_cost = (g_cost + time_weight * data['time_norm'] + 
                          price_weight * data['price_norm'] + 
                          emissions_weight * data['emissions_norm'] + 
                          border_penalty)
            h_cost = heuristic_dict[neighbor]
            new_f_cost = new_g_cost + h_cost

            new_path = path + [neighbor]
            new_edge_details = edge_details + [(current, neighbor, key, data)]

            counter += 1
            heapq.heappush(queue, (new_f_cost, new_g_cost, counter, neighbor, new_path, new_edge_details, new_wait_time))
    
    completed_paths.sort(key=lambda x: x[2])
    if not completed_paths:
        return {"error": f"No paths found between {start} and {goal} with selected parameters."}
    
    return [{
        "path": path,
        "path_coords": [(multigraph.nodes[node]['latitude'], multigraph.nodes[node]['longitude']) for node in path],
        "edges": [{
            "from": edge[0], 
            "to": edge[1], 
            "mode": edge[3]['mode'],
            "time": edge[3]['time'], 
            "price": edge[3]['price'], 
            "distance": edge[3]['distance'],
            "co2_per_ton": edge[3]['distance'] * EMISSION_FACTORS[edge[3]['mode']]
        } for edge in edges],
        "total_time": sum(edge[3]['time'] for edge in edges),
        "total_cost": sum(edge[3]['price']/100 for edge in edges) * (weight / 995 if weight < 995 else (weight - 995) * 2),
        "total_distance": sum(edge[3]['distance'] for edge in edges),
        "total_co2": sum(edge[3]['distance'] * EMISSION_FACTORS[edge[3]['mode']] * (weight / 100000) for edge in edges),
        "waiting_time": wait_time,
        "sustainability_score": calculate_sustainability_score(sum(edge[3]['distance'] * EMISSION_FACTORS[edge[3]['mode']] * (weight / 500) for edge in edges))
    } for path, edges, cost, wait_time in completed_paths[:top_n]]

def calculate_sustainability_score(co2_emissions):
    # Simple scoring system: lower CO2 = higher score (0-100)
    max_co2 = 5000  # Assume 5000kg as max for normalization
    score = max(0, 100 - (co2_emissions / max_co2 * 100))
    return round(score, 2)

# Streamlit UI
st.title("🌍 Sustainable Route Planner")
st.markdown("""
    Plan your shipping routes with climate change in mind. Minimize your carbon footprint 
    while balancing time and cost. Every choice counts in building a greener future!
""")

# Input form
with st.form("route_form"):
    col1, col2 = st.columns(2)
    with col1:
        start = st.text_input("Starting Location", "Jalgaon")
        goal = st.text_input("Destination", "San Francisco")
        weight = st.number_input("Cargo Weight (kg)", min_value=0, value=100)
    
    with col2:
        avoid_countries = st.multiselect("Countries to Avoid", 
                                       options=['CN', 'US', 'BR', 'IN', 'RU'],
                                       default=[])
        allowed_modes = st.multiselect("Allowed Transport Modes", 
                                     options=['land', 'sea', 'air'],
                                     default=['land', 'sea', 'air'])

    st.subheader("Route Optimization Priorities")
    col3, col4, col5 = st.columns(3)
    with col3:
        emissions_weight = st.slider("CO2 Emissions Priority", 0.0, 1.0, 0.5, 
                                   help="Higher value prioritizes lower carbon emissions")
    with col4:
        time_weight = st.slider("Time Priority", 0.0, 1.0, 0.25)
    with col5:
        price_weight = st.slider("Cost Priority", 0.0, 1.0, 0.25)

    cargo_desc = st.text_input("Cargo Description", "Perishable")
    submitted = st.form_submit_button("Find Sustainable Routes")

if submitted:
    total_weight = time_weight + price_weight + emissions_weight
    if abs(total_weight - 3.0) > 5:
        st.error("Priorities must sum to less than 3.0. Please adjust the sliders.")
    else:
        with st.spinner("Calculating sustainable routes..."):
            results = astar_top_n_avoid_countries(
                roadsn, start, goal, avoid_countries=avoid_countries,
                top_n=3, time_weight=time_weight, price_weight=price_weight,
                emissions_weight=emissions_weight, allowed_modes=allowed_modes,
                weight=weight
            )
        
        if "error" in results:
            st.error(results["error"])
        else:
            st.success("✅ Routes calculated with sustainability in focus!")
            
            for i, path in enumerate(results, 1):
                with st.expander(f"Route {i} - Sustainability Score: {path['sustainability_score']}/100"):
                    # Visualize route on map
                    fig = go.Figure(go.Scattergeo(
                        lon=[coord[1] for coord in path['path_coords']],
                        lat=[coord[0] for coord in path['path_coords']],
                        mode='lines+markers',
                        line=dict(width=2, color='green'),
                        marker=dict(size=8)
                    ))
                    fig.update_layout(
                        title=f"Route {i} Map",
                        geo=dict(showcoastlines=True, landcolor="rgb(243, 243, 243)")
                    )
                    st.plotly_chart(fig)

                    # Display metrics
                    st.metric("Total CO2 Emissions", f"{path['total_co2']:.2f} kg")
                    st.metric("Total Time", f"{path['total_time']:.2f} hours")
                    st.metric("Total Cost", f"${path['total_cost']:.2f}")
                    st.metric("Distance", f"{path['total_distance']:.2f} km")

                    # Detailed breakdown
                    df = pd.DataFrame(path['edges'])
                    st.dataframe(df.style.format({
                        'time': '{:.2f}',
                        'price': '{:.2f}',
                        'distance': '{:.2f}',
                        'co2_per_ton': '{:.2f}'
                    }))

                    # Sustainability insights
                    co2 = path['total_co2']
                    if co2 > 1000:
                        st.warning("⚠️ High carbon footprint! Consider using more sea transport.")
                    elif co2 < 500:
                        st.success("🌱 Great choice! Low carbon emissions route.")

st.sidebar.markdown("""
### 🌿 Sustainability Tips
- Prioritize sea transport for lowest emissions
- Minimize air transport where possible
- Optimize cargo weight to reduce CO2 per kg
- Avoid unnecessary detours
""")
