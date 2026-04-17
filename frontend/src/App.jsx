import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { UserPlus, Settings, Activity, Trash2 } from 'lucide-react';
import './App.css';

const API_BASE = 'http://localhost:8000/api';

function App() {
  const [employees, setEmployees] = useState([]);
  const [newEmp, setNewEmp] = useState({ name: '', role: '', description: '' });

  const fetchEmployees = async () => {
    try {
      const res = await axios.get(`${API_BASE}/employees`);
      setEmployees(res.data.employees);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchEmployees();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE}/employees`, newEmp);
      setNewEmp({ name: '', role: '', description: '' });
      fetchEmployees();
    } catch (e) {
      alert("Failed to create employee");
    }
  };

  const handleDelete = async (name) => {
    try {
      await axios.delete(`${API_BASE}/employees/${name}`);
      fetchEmployees();
    } catch (e) {
      alert("Failed to delete employee");
    }
  };

  const handleStartGateway = async (name) => {
    try {
      await axios.post(`${API_BASE}/employees/${name}/gateway/start`);
      alert(`Gateway for ${name} started!`);
    } catch (e) {
      alert("Failed to start gateway");
    }
  };

  return (
    <div className="container">
      <header>
        <h1>安消大脑 Control Plane</h1>
        <p>Digital Employee Management System</p>
      </header>

      <main>
        <section className="create-section">
          <h2><UserPlus size={20} /> 构建岗位数字员工</h2>
          <form onSubmit={handleCreate}>
            <input 
              placeholder="Name (e.g., SecurityGuard_01)" 
              value={newEmp.name}
              onChange={e => setNewEmp({...newEmp, name: e.target.value})}
              required 
            />
            <input 
              placeholder="Role (e.g., 消防巡查员)" 
              value={newEmp.role}
              onChange={e => setNewEmp({...newEmp, role: e.target.value})}
              required 
            />
            <textarea 
              placeholder="Description & Responsibilities" 
              value={newEmp.description}
              onChange={e => setNewEmp({...newEmp, description: e.target.value})}
              required 
            />
            <button type="submit">Create Employee</button>
          </form>
        </section>

        <section className="list-section">
          <h2><Activity size={20} /> 员工状态与综合调度</h2>
          <div className="grid">
            {employees.map(emp => (
              <div key={emp.name} className="card">
                <h3>{emp.name}</h3>
                <span className="badge">{emp.status}</span>
                <div className="soul-preview">
                  <strong>SOUL:</strong>
                  <pre>{emp.soul}</pre>
                </div>
                <div className="actions">
                  <button onClick={() => handleStartGateway(emp.name)}>
                    <Settings size={14} /> 启动微信网关
                  </button>
                  <button className="danger" onClick={() => handleDelete(emp.name)}>
                    <Trash2 size={14} /> 离职 (Delete)
                  </button>
                </div>
              </div>
            ))}
            {employees.length === 0 && <p>No digital employees found.</p>}
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
