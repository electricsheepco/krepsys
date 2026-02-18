import { BrowserRouter as Router } from 'react-router-dom'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <div className="flex h-screen">
          {/* Sidebar will go here */}
          <div className="w-64 bg-white border-r border-gray-200 p-4">
            <h1 className="text-2xl font-bold text-gray-800">Krepsys</h1>
            <p className="text-sm text-gray-500 mt-1">Newsletter Reader</p>
          </div>

          {/* Main content will go here */}
          <div className="flex-1 flex flex-col">
            <div className="p-8">
              <h2 className="text-3xl font-bold text-gray-800">Welcome to Krepsys</h2>
              <p className="text-gray-600 mt-2">Your self-hosted newsletter reader</p>
              <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-blue-800">Frontend setup complete!</p>
                <p className="text-blue-600 text-sm mt-1">Ready to build components</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Router>
  )
}

export default App
