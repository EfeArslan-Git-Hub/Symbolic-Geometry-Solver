from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sympy
from sympy import symbols, solve, sympify, Eq, latex, diff, integrate, limit, oo, sqrt, Abs, Max
import re
import numpy as np
import json
import plotly.graph_objects as go
import plotly.utils

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProblemInput(BaseModel):
    problem: str

def get_plotly_json(fig):
    return json.loads(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))

def solve_physics(problem_str: str):
    p = problem_str.lower()
    if "projectile" in p:
        v_match = re.search(r'velocity\s*(\d+\.?\d*)', p)
        a_match = re.search(r'angle\s*(\d+\.?\d*)', p)
        
        if v_match and a_match:
            v0 = float(v_match.group(1))
            angle_deg = float(a_match.group(1))
            theta = np.radians(angle_deg)
            g = 9.81
            
            t_flight = (2 * v0 * np.sin(theta)) / g
            h_max = (v0**2 * (np.sin(theta)**2)) / (2 * g)
            r_max = (v0**2 * np.sin(2 * theta)) / g
            
            t = np.linspace(0, t_flight, 100)
            x = v0 * np.cos(theta) * t
            y = v0 * np.sin(theta) * t - 0.5 * g * t**2
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='Trajectory', line=dict(color='orange', width=3)))
            fig.add_trace(go.Scatter(x=[r_max/2], y=[h_max], mode='markers+text', 
                                     text=[f'Max Height: {round(h_max,2)}m'], textposition="top center",
                                     marker=dict(color='red', size=8), name='Peak'))
            fig.add_trace(go.Scatter(x=[r_max], y=[0], mode='markers+text',
                                     text=[f'Range: {round(r_max,2)}m'], textposition="bottom right",
                                     marker=dict(color='green', size=8), name='Impact'))

            fig.update_layout(
                title=f'Projectile Motion (v0={v0}m/s, θ={angle_deg}°)',
                xaxis_title='Distance (m)',
                yaxis_title='Height (m)',
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            
            return {
                "solution_latex": f"R = {latex(round(r_max,2))}m, \\quad H_{{max}} = {latex(round(h_max,2))}m",
                "steps": [
                    f"**Step 1: Identify Parameters**\\\\Initial Velocity $v_0 = {v0}$ m/s, Angle $\\theta = {angle_deg}^\\circ$.",
                    f"**Step 2: Physics Principles**\\\\Decompose motion into horizontal (constant speed) and vertical (gravity affected) components.",
                    f"**Step 3: Horizontal Range Formula**\\\\$R = \\frac{{v_0^2 \\sin(2\\theta)}}{{g}} = \\frac{{{v0}^2 \\sin({2*angle_deg}^\\circ)}}{{9.81}} \\approx {round(r_max,2)}$ m.",
                    f"**Step 4: Max Height Formula**\\\\$H = \\frac{{v_0^2 \\sin^2(\\theta)}}{{2g}} \\approx {round(h_max,2)}$ m."
                ],
                "plotData": get_plotly_json(fig)
            }
    return None

def solve_3d(problem_str: str):
    p = problem_str.strip().lower()

    if "distance" in p:
        points = re.findall(r'\(\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*\)', p)
        if len(points) == 2:
            x1, y1, z1 = map(float, points[0])
            x2, y2, z2 = map(float, points[1])
            dist = sympy.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter3d(
                x=[x1, x2], y=[y1, y2], z=[z1, z2],
                mode='lines+markers', marker=dict(size=5, color='cyan'),
                line=dict(color='cyan', width=5), name='Distance'
            ))
            fig.add_trace(go.Scatter3d(x=[x1, x2], y=[y1, y2], z=[min(z1,z2), min(z1,z2)], mode='lines', line=dict(dash='dash', color='gray'), name='Ground Projection'))

            fig.update_layout(
                title='3D Euclidean Distance',
                scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'),
                template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, b=0, t=40)
            )
            
            return {
                "solution_latex": f"d = {latex(dist.evalf(4))}",
                "steps": [
                    "**Step 1: Identify Coordinates**\\\\Points $A({x1}, {y1}, {z1})$ and $B({x2}, {y2}, {z2})$.",
                    "**Step 2: Distance Formula (3D)**\\\\$d = \\sqrt{(x_2-x_1)^2 + (y_2-y_1)^2 + (z_2-z_1)^2}$.", 
                    f"**Step 3: Calculation**\\\\$d \\approx {round(float(dist), 4)}$."
                ],
                "plotData": get_plotly_json(fig)
            }
            
    if "sphere" in p:
        match = re.search(r'radius\s*(\d+\.?\d*)', p)
        if match:
            r = float(match.group(1))
            vol = (4/3) * sympy.pi * r**3
            area = 4 * sympy.pi * r**2
            
            theta = np.linspace(0, 2*np.pi, 50)
            phi = np.linspace(0, np.pi, 50)
            x = r * np.outer(np.cos(theta), np.sin(phi))
            y = r * np.outer(np.sin(theta), np.sin(phi))
            z = r * np.outer(np.ones(50), np.cos(phi))
            
            fig = go.Figure(data=[go.Surface(x=x, y=y, z=z, opacity=0.8, colorscale='Viridis')])
            fig.update_layout(title=f'Sphere (r={r})', scene=dict(aspectmode='data'), template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, b=0, t=40))
            
            return {
                "solution_latex": f"V = {latex(vol.evalf(4))} \\\\ A = {latex(area.evalf(4))}",
                "steps": [
                    f"**Step 1: Identify Radius**\\\\$r = {r}$.",
                    "**Step 2: Volume Formula**\\\\$V = \\frac{4}{3}\\pi r^3$.",
                    "**Step 3: Surface Area Formula**\\\\$A = 4\\pi r^2$."
                ],
                "plotData": get_plotly_json(fig)
            }

    return None

def solve_distance(problem_str: str):
    p = problem_str.strip().lower()
    points = re.findall(r'\(\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*\)', p)
    if len(points) != 2: return None
        
    x1, y1 = float(points[0][0]), float(points[0][1])
    x2, y2 = float(points[1][0]), float(points[1][1])
    
    metric = "euclidean"
    if "taxicab" in p: metric = "taxicab"
    elif "chebyshev" in p: metric = "chebyshev"
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[x1, x2], y=[y1, y2], mode='markers+text', text=['A', 'B'], textposition="bottom center", marker=dict(size=10, color='white')))

    result_latex = ""
    steps = []
    
    if metric == "euclidean":
        dist = sympy.sqrt((x2-x1)**2 + (y2-y1)**2)
        fig.add_trace(go.Scatter(x=[x1, x2], y=[y1, y2], mode='lines', line=dict(color='cyan', width=3), name='Euclidean'))
        result_latex = f"{latex(dist.evalf(4))}"
        steps = [
            "**Step 1: Euclidean Distance Formula**\\\\$d = \\sqrt{(x_2-x_1)^2 + (y_2-y_1)^2 + (z_2-z_1)^2}$.",
            f"**Step 2: Substitute**\\\\$d = \\sqrt{{({x2}-{x1})^2 + ({y2}-{y1})^2}}$.",
            f"**Result**\\\\$d \\approx {round(float(dist), 4)}$"
        ]
        
    elif metric == "taxicab":
        dist = abs(x2-x1) + abs(y2-y1)
        fig.add_trace(go.Scatter(x=[x1, x2, x2], y=[y1, y1, y2], mode='lines', line=dict(color='red', width=3, shape='hv'), name='Taxicab'))
        result_latex = f"{dist}"
        steps = [
            "**Step 1: Taxicab (L1) Formula**\\\\$d = |x_2-x_1| + |y_2-y_1|$.",
            f"**Result**\\\\$d = |{x2}-{x1}| + |{y2}-{y1}| = {dist}$"
        ]

    elif metric == "chebyshev":
        dist = max(abs(x2-x1), abs(y2-y1))
        fig.add_shape(type="rect", x0=x1, y0=y1, x1=x1+(x2-x1), y1=y1+(y2-y1), line=dict(color="green"), fillcolor="green", opacity=0.2)
        fig.add_trace(go.Scatter(x=[x1, x2], y=[y1, y2], mode='lines', line=dict(color='green', dash='dot'), name='Chebyshev'))
        result_latex = f"{dist}"
        steps = [
            "**Step 1: Chebyshev (L∞) Formula**\\\\$d = \\max(|x_2-x_1|, |y_2-y_1|)$.",
            f"**Result**\\\\$d = \\max(|{x2-x1}|, |{y2-y1}|) = {dist}$"
        ]

    fig.update_layout(title=f'{metric.capitalize()} Distance', template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))

    return {
        "solution_latex": f"d = {result_latex}",
        "steps": steps,
        "plotData": get_plotly_json(fig)
    }

def solve_geometry(problem_str: str):
    p = problem_str.strip().lower()
    match = re.search(r'(hypotenuse|triangle).*sides.*?(\d+\.?\d*).*?(\d+\.?\d*)', p)
    if match:
        a = float(match.group(2))
        b = float(match.group(3))
        c = sympy.sqrt(a**2 + b**2)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[0, b, 0, 0], y=[0, 0, a, 0], mode='lines', line=dict(color='cyan', width=3), name='Triangle'))
        fig.add_trace(go.Scatter(x=[0, b, 0, 0], y=[0, 0, a, 0], fill='toself', fillcolor='rgba(0, 255, 255, 0.2)', line=dict(width=0), showlegend=False))
        fig.add_trace(go.Scatter(x=[b/2, -0.1*b, b/2], y=[-0.1*a, a/2, a/2], mode='text', 
                                 text=[f'b={b}', f'a={a}', f'c={round(float(c),2)}'],
                                 textposition="middle center", textfont=dict(color='white')))

        fig.update_layout(
            title='Right Triangle',
            xaxis=dict(scaleanchor="y", scaleratio=1),
            yaxis=dict(constrain="domain"),
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        
        return {
            "solution_latex": f"c = {latex(c.evalf(4))}",
            "steps": [
                f"**Step 1: Identify Given Sides**\\\\Legs are $a={a}$ and $b={b}$.",
                "**Step 2: Apply Pythagorean Theorem**\\\\For a right triangle, $a^2 + b^2 = c^2$.",
                f"**Step 3: Substitute & Solve**\\\\$c = \\sqrt{{{a}^2 + {b}^2}} = \\sqrt{{{a**2} + {b**2}}} = {latex(c.evalf(4))}$."
            ],
            "plotData": get_plotly_json(fig)
        }
    return None

def solve_calculus(problem_str: str):
    x = symbols('x')
    p = problem_str.lower()
    
    if "derivative" in p or "diff" in p:
         expr_str = re.sub(r'(derivative|diff)\s*', '', problem_str, flags=re.IGNORECASE)
         expr = sympify(expr_str)
         res = diff(expr, x)
         
         try:
            f = sympy.lambdify(x, expr, "numpy")
            fp = sympy.lambdify(x, res, "numpy")
            x_vals = np.linspace(-5, 5, 200)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x_vals, y=f(x_vals), name=f'f(x)={expr}', line=dict(dash='dash', color='blue')))
            fig.add_trace(go.Scatter(x=x_vals, y=fp(x_vals), name=f"f'(x)={res}", line=dict(color='red')))
            fig.update_layout(title="Derivative", template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
            plot_data = get_plotly_json(fig)
         except: plot_data = None
         
         steps = [f"**Step 1: Identify Function**\\\\$f(x) = {latex(expr)}$"]
         if expr.is_Add:
             steps.append("**Step 2: Sum Rule**\\\\The derivative of a sum is the sum of the derivatives: $\\frac{d}{dx}[f(x) + g(x)] = f'(x) + g'(x)$.")
         if expr.is_Pow:
             steps.append("**Step 2: Power Rule**\\\\Apply $\\frac{d}{dx}x^n = nx^{n-1}$.")
         steps.append(f"**Step 3: Compute**\\\\$f'(x) = {latex(res)}$")

         return {"solution_latex": latex(res), "steps": steps, "plotData": plot_data}

    if "integrate" in p or "integral" in p:
         expr_str = re.sub(r'(integrate|integral)\s*', '', problem_str, flags=re.IGNORECASE)
         expr = sympify(expr_str)
         res = integrate(expr, x)
         
         try:
            f = sympy.lambdify(x, expr, "numpy")
            fi = sympy.lambdify(x, res, "numpy")
            x_vals = np.linspace(-5, 5, 200)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x_vals, y=f(x_vals), name=f'f(x)', line=dict(dash='dash', color='blue')))
            fig.add_trace(go.Scatter(x=x_vals, y=fi(x_vals), name=f"Int(f)", line=dict(color='green')))
            fig.update_layout(title="Integration", template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
            plot_data = get_plotly_json(fig)
         except: plot_data = None
         
         steps = [f"**Step 1: Identify Function**\\\\$f(x) = {latex(expr)}$"]
         steps.append("**Step 2: Find Antiderivative**\\\\Look for a function $F(x)$ such that $F'(x) = f(x)$.")
         steps.append(f"**Step 3: Result**\\\\$\\int f(x) dx = {latex(res)} + C$")
         
         return {"solution_latex": f"{latex(res)} + C", "steps": steps, "plotData": plot_data}
         
    return None

def solve_algebra(problem_str: str):
    x = symbols('x')
    try:
        if "=" in problem_str:
            l, r = problem_str.split("=", 1)
            eq = Eq(sympify(l), sympify(r))
        else:
            eq = sympify(problem_str)
        
        sol = solve(eq)
        expr = eq.lhs - eq.rhs if isinstance(eq, Eq) else eq
        f = sympy.lambdify(x, expr, "numpy")
        x_vals = np.linspace(-10, 10, 400)
        y_vals = f(x_vals)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_vals, y=y_vals, name='f(x)', line=dict(color='purple')))
        fig.add_shape(type="line", x0=-10, x1=10, y0=0, y1=0, line=dict(color="white", width=1)) 
        for s in sol:
            if s.is_real: fig.add_trace(go.Scatter(x=[float(s)], y=[0], mode='markers', marker=dict(size=10, color='yellow'), name='Root'))
        fig.update_layout(title="Solution", template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
        
        return {
            "solution_latex": latex(sol),
            "steps": [
                f"**Step 1: Setup Equation**\\\\${latex(eq)}$",
                "**Step 2: Isolate Variable**\\\\Move terms to solve for $x$.",
                f"**Step 3: Solve**\\\\$x = {latex(sol)}$"
            ],
            "plotData": get_plotly_json(fig)
        }
    except: return None

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Symbolic Geometry Solver Backend is Running"}

@app.post("/solve")
async def solve_problem(input_data: ProblemInput):
    p = input_data.problem
    try:
        # Priority Order
        if "projectile" in p.lower(): return solve_physics(p)
        if "distance" in p.lower() and "3d" not in p.lower(): return solve_distance(p)
        if "3d" in p.lower() or "sphere" in p.lower(): return solve_3d(p)
        
        calc_res = solve_calculus(p)
        if calc_res: return calc_res
        
        geo_res = solve_geometry(p)
        if geo_res: return geo_res
        
        alg_res = solve_algebra(p)
        if alg_res: return alg_res
        
        return {"solution_latex": "\\text{Could not interpret query}", "steps": ["Try 'help' or check examples."], "plotData": None}

    except Exception as e:
        return {"solution_latex": "\\text{Error}", "steps": [str(e)], "plotData": None}
