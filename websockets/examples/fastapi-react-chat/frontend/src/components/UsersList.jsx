import './UsersList.css'

function UsersList({ users, currentUsername }) {
  return (
    <div className="users-sidebar">
      <h3>En línea ({users.length})</h3>
      <div className="users-list">
        {users.map((user) => (
          <div
            key={user.id}
            className={`user-item ${user.username === currentUsername ? 'current' : ''}`}
          >
            <span className="user-dot"></span>
            <span className="user-name">{user.username}</span>
            {user.username === currentUsername && (
              <span className="you-badge">Tú</span>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default UsersList
