  // Função para atualizar o local storage ao selecionar ou desselecionar um checkbox
  function updateLocalStorage(checkbox) {
      let selectedDates = JSON.parse(localStorage.getItem('selectedDates')) || [];
      if (checkbox.checked) {
          if (!selectedDates.includes(checkbox.value)) {
              selectedDates.push(checkbox.value);
          }
      } else {
          selectedDates = selectedDates.filter(id => id !== checkbox.value);
      }

      localStorage.setItem('selectedDates', JSON.stringify(selectedDates));
  }

  // Função para carregar seleções do local storage ao carregar a página e marcar as coletas se estiver presente no localStorage
  function loadSelections() {
      let selectedDates = JSON.parse(localStorage.getItem('selectedDates')) || [];
      document.querySelectorAll('input[name="dates[]"]').forEach(checkbox => {
        checkbox.checked = selectedDates.includes(checkbox.value);
      });
  }

  // Adicionar evento de carregar seleções ao carregar a página
  document.addEventListener('DOMContentLoaded', loadSelections);

  // Adicionar todas as seleções ao campo hidden antes de submeter o formulário
  document.getElementById('dataForm').addEventListener('submit', function(event) {
      let selectedDates = JSON.parse(localStorage.getItem('selectedDates')) || [];
      selectedDates.forEach(date => {
          let input = document.createElement('input');
          input.type = 'hidden';
          input.name = 'dates[]';
          input.value = date;
          this.appendChild(input);
      });
  });

  console.log(localStorage.getItem('selectedDates'));


  // Função para limpar apenas as seleções do localStorage
  function clearLocalStorageSelections() {
      localStorage.removeItem('selectedDates');
  }

    // Inicializamos nextPageIsPagination como false
    let nextPageIsPagination = false;

    // Adicionar evento para marcar que o próximo carregamento será por paginação ao clicar na paginação
    document.querySelectorAll('.pagination a').forEach(link => {
        link.addEventListener('click', function() {
            nextPageIsPagination = true;
        });
    });

    // Adicionar evento de clique ao botão "Próximo" para definir nextPageIsPagination como true
    document.getElementById('btnProximo').addEventListener('click', function() {
        nextPageIsPagination = true;
    });


    // Adicionar evento para limpar apenas as seleções do localStorage ao recarregar a página pelo navegador
    window.addEventListener('unload', function(event) {
        // Verificar se o próximo carregamento não será feito por paginação
        if (!nextPageIsPagination) {
            clearLocalStorageSelections();
        }
    });
