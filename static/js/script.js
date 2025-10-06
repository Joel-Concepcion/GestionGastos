
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="mensaje"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl)
})

document.addEventListener('DOMContentLoaded', function () {
    const gastoForm = document.getElementById('gastoForm');
    const submitBtn = document.getElementById('submitBtn');

    // Función para cargar datos en el formulario para edición

    document.querySelectorAll('.edit-btn').forEach(button => {
        //document.getElementById('tipo').value = gasto.tipo;
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const id_gasto = this.getAttribute('data-id');

            fetch(`/get_gasto/${id_gasto}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const gasto = data.gasto;

                        // Aquí ya puedes usar gasto.tipo sin errores
                        document.getElementById('tipo').value = gasto.tipo || '';

                        // Resto del formulario
                        document.getElementById('gastoId').value = gasto.id_gasto;
                        document.getElementById('categoria').value = gasto.categoria || '';
                        document.getElementById('monto').value = gasto.monto || '';
                        document.getElementById('fecha').value = gasto.fecha || '';
                        document.getElementById('descripcion').value = gasto.descripcion || '';
                        submitBtn.textContent = 'Guardar cambios';
                    } else {
                        Swal.fire('Error', data.message || 'No se pudo cargar el gasto.', 'error');
                    }
                })
        });
    });

    // Función para eliminar un gasto
    document.querySelectorAll('.delete-btn').forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const id_gasto = this.getAttribute('data-id');

            Swal.fire({
                title: '¿Eliminar este gasto?',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Sí, eliminar',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    fetch(`/delete/${id_gasto}`, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                this.closest('tr').remove();
                                Swal.fire('Eliminado', data.message, 'success');
                            } else {
                                Swal.fire('Error', data.message, 'error');
                            }
                        })
                        .catch(error => {
                            Swal.fire('Error', 'Ocurrió un problema al eliminar.', 'error');
                        });
                }
            });
        });
    });

    // Manejar el envío del formulario (registrar o actualizar)
    gastoForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const id_gasto = document.getElementById('gastoId').value;

        fetch('/control', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams(new FormData(this)).toString()
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Swal.fire('Éxito', data.message, 'success').then(() => {
                        location.reload(); // Recargar para reflejar cambios
                    });
                } else {
                    Swal.fire('Error', data.message, 'error');
                }
            })
            .catch(error => {
                Swal.fire('Error', 'Ocurrió un problema al guardar.', 'error');
            });
    });
});

