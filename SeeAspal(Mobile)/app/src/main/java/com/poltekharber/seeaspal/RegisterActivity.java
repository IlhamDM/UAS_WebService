//6D 18090122 Dimas Ilham Mardiyanto
//6D 18090139 Alfan Nur Rabbani
package com.poltekharber.seeaspal;

import androidx.appcompat.app.AppCompatActivity;

import android.content.ContentValues;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

public class RegisterActivity extends AppCompatActivity {
    EditText TxName, TxUsername, TxPassword;
    Button BtnRegister;
    DBHelper dbHelper;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_register);

        dbHelper = new DBHelper(this);

        TxName = (EditText)findViewById(R.id.editTextTextPersonName2);
        TxUsername = (EditText)findViewById(R.id.editTextTextPersonName3);
        TxPassword = (EditText)findViewById(R.id.editTextTextPassword2);
        BtnRegister = (Button)findViewById(R.id.btnRegister);

        TextView tvLoginAcc = (TextView)findViewById(R.id.tvLogin);

        tvLoginAcc.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                startActivity(new Intent(RegisterActivity.this, LoginActivity.class));
            }
        });

        BtnRegister.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                String name = TxName.getText().toString().trim();
                String username = TxUsername.getText().toString().trim();
                String password = TxPassword.getText().toString().trim();

                ContentValues values = new ContentValues();

                if(password.equals("") || username.equals("")){
                    Toast.makeText(RegisterActivity.this, "Username/Password cannot be empty", Toast.LENGTH_SHORT).show();
                } else {
                    values.put(DBHelper.row_name, name);
                    values.put(DBHelper.row_username, username);
                    values.put(DBHelper.row_password, password);

                    dbHelper.insertData(values);

                    Toast.makeText(RegisterActivity.this, "Register Successfull", Toast.LENGTH_SHORT).show();
                    finish();
                }
            }
        });
    }

}