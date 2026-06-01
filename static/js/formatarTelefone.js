document.addEventListener("DOMContentLoaded", function () {
  const telefoneInput = document.getElementById("formTelefone");

  if (!telefoneInput) {
    return;
  }

  function aplicarMascaraTelefone(valor) {
    valor = valor.replace(/\D/g, "").slice(0, 11);

    if (valor.length === 0) {
      return "";
    }

    if (valor.length <= 2) {
      return "(" + valor;
    }

    if (valor.length <= 6) {
      return "(" + valor.slice(0, 2) + ") " + valor.slice(2);
    }

    if (valor.length <= 10) {
      return "(" + valor.slice(0, 2) + ") " + valor.slice(2, 6) + "-" + valor.slice(6);
    }

    return "(" + valor.slice(0, 2) + ") " + valor.slice(2, 7) + "-" + valor.slice(7);
  }

  telefoneInput.addEventListener("input", function () {
    telefoneInput.value = aplicarMascaraTelefone(telefoneInput.value);
  });

  telefoneInput.value = aplicarMascaraTelefone(telefoneInput.value);
});