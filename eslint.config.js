import globals from 'globals';

export default [
  {
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
        frappe: true,
        cur_frm: true,
        cur_dialog: true,
        cur_page: true,
        __: true,
        $: true,
        jQuery: true
      },
      ecmaVersion: 'latest',
      sourceType: 'module'
    },
    rules: {
      'no-unused-vars': 'off',
      'no-console': 'warn',
      'quotes': 'off',
      'semi': 'off',
      'camelcase': 'off',
      'no-useless-escape': 'off',
      'no-extra-boolean-cast': 'off',
      'indent': 'off',
      'brace-style': 'off',
      'no-mixed-spaces-and-tabs': 'off',
      'linebreak-style': 'off'
    }
  }
];