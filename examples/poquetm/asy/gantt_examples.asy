settings.outformat = "pdf";
unitsize(1cm);
from job access *;

Job[] generate_workload()
{
    Job j1, j2, j3, j4;

    j1.id = "$1$";
    j1.submission_date = 0;
    j1.processing_time = 2;
    j1.requested_time = 3;
    j1.number_of_requested_resources = 2;
    j1.fill_color = rgb(251,180,174);

    j2.id = "$2$";
    j2.submission_date = 0;
    j2.processing_time = 1;
    j2.requested_time = 2;
    j2.number_of_requested_resources = 2;
    j2.fill_color = rgb(179,205,227);

    j3.id = "$3$";
    j3.submission_date = 1;
    j3.processing_time = 3;
    j3.requested_time = 5;
    j3.number_of_requested_resources = 2;
    j3.fill_color = rgb(204,235,197);

    j4.id = "$4$";
    j4.submission_date = 3;
    j4.processing_time = 1;
    j4.requested_time = 2;
    j4.number_of_requested_resources = 4;
    j4.fill_color = rgb(222,203,228);

    Job jobs[] = {j1, j2, j3, j4};
    return jobs;
}

Job[] generate_energy_jobs()
{
    Job json, jsoff, joff;

    json.id = "on";
    json.processing_time = 2;
    json.number_of_requested_resources = 1;
    json.fill_color = rgb("56ae6c");

    jsoff.id = "off";
    jsoff.processing_time = 1;
    jsoff.number_of_requested_resources = 1;
    jsoff.fill_color = rgb("ba495b");

    joff.id = "";
    joff.processing_time = 2;
    joff.number_of_requested_resources = 1;
    joff.fill_color = rgb("444444");

    Job[] jobs = {json, jsoff, joff};
    return jobs;
}

void figure_workload_example()
{
    // Let's define the jobs
    Job jobs[] = generate_workload();
    Job energy_jobs[] = generate_energy_jobs();
    Job j1, j2, j3, j4, json, jsoff, joff;

    j1 = jobs[0];
    j2 = jobs[1];
    j3 = jobs[2];
    j4 = jobs[3];
    json = energy_jobs[0];
    jsoff = energy_jobs[1];
    joff = energy_jobs[2];

    joff.processing_time = 4;

    // Let's draw the jobs
    real base_y = 0;

    draw_job_on_position(j1, (0,base_y+2.5), draw_requested_time=true);
    draw_job_on_position(j2, (3.5,base_y+2.5), draw_requested_time=true);
    draw_job_on_position(j3, (0,base_y+0), draw_requested_time=true);
    draw_job_on_position(j4, (6,base_y+0.5), draw_requested_time=true);
    draw_job_on_position(json, (9,base_y+3.5));
    draw_job_on_position(jsoff, (9.5,base_y+1.5));
    draw_job_on_position(joff, (6.5, base_y-0.75));

    // Let's draw the submission times
    draw_frame(0,3, base_y-1.5,0,
               draw_machines_axe = false,
               draw_machines_separations = false);

    for (int i = 0; i < jobs.length; ++i)
    {
        draw((jobs[i].submission_date, base_y-1) --
             (jobs[i].submission_date, base_y-1.5), Arrow);
    }

    label("$r_1$", (j1.submission_date, base_y-1), align=up);
    label("$r_2$", (j2.submission_date, base_y-0.6), align=up);
    label("$r_3$", (j3.submission_date, base_y-1), align=up);
    label("$r_4$", (j4.submission_date, base_y-1), align=up);

    // Let's draw q_j
    draw((0-0.25, base_y+2.5) -- (0-0.25, base_y+2.5+j1.number_of_requested_resources), Arrow);
    draw((0-0.25, base_y+2.5) -- (0-0.25, base_y+2.5+j1.number_of_requested_resources) -- cycle, Arrow);
    label((string)j1.number_of_requested_resources, (0-0.25, base_y+2.5+(j1.number_of_requested_resources/2.0)), align=left);

    draw((0-0.25, base_y+0) -- (0-0.25, base_y+0+j3.number_of_requested_resources), Arrow);
    draw((0-0.25, base_y+0) -- (0-0.25, base_y+0+j3.number_of_requested_resources) -- cycle, Arrow);
    label((string)j3.number_of_requested_resources, (0-0.25, base_y+0+(j3.number_of_requested_resources/2.0)), align=left);

    draw((6+j4.requested_time+0.25, base_y+0.5) -- (6+j4.requested_time+0.25, base_y+0.5+j4.number_of_requested_resources), Arrow);
    draw((6+j4.requested_time+0.25, base_y+0.5) -- (6+j4.requested_time+0.25, base_y+0.5+j4.number_of_requested_resources) -- cycle, Arrow);
    label((string)j4.number_of_requested_resources, (6+j4.requested_time+0.25, base_y+0.5+(j4.number_of_requested_resources/2.0)), align=right);

    // Let's draw p_j of switch jobs
    draw((9,base_y+3.5-0.25) -- (9+json.processing_time,base_y+3.5-0.25), black, Arrow);
    draw((9,base_y+3.5-0.25) -- (9+json.processing_time,base_y+3.5-0.25) -- cycle, black, Arrow);
    label((string)json.processing_time, (9+(json.processing_time/2.0),base_y+3.5-0.25), align=down);

    draw((9.5, base_y+1.5-0.25) -- (9.5+jsoff.processing_time,base_y+1.5-0.25), black, Arrow);
    draw((9.5, base_y+1.5-0.25) -- (9.5+jsoff.processing_time,base_y+1.5-0.25) -- cycle, black, Arrow);
    label((string)jsoff.processing_time, (9.5+(jsoff.processing_time/2.0),base_y+1.5-0.25), align=down);

    draw((6.5, base_y-0.75-0.25) -- (6.5+joff.processing_time,base_y-0.75-0.25), black, Arrow);
    draw((6.5, base_y-0.75-0.25) -- (6.5+joff.processing_time,base_y-0.75-0.25) -- cycle, black, Arrow);
    label("$\ge0$", (6.5+(joff.processing_time/2.0),base_y-0.75-0.25), align=down);

    shipout("workload_example");
}

void figure_gantt_easy()
{
    // Let's define the jobs
    Job jobs[] = generate_workload();
    Job j1, j2, j3, j4;

    j1 = jobs[0];
    j2 = jobs[1];
    j3 = jobs[2];
    j4 = jobs[3];

    // Let's draw the frame
    draw_frame(0,6, 0,4);

    // Let's draw the jobs
    draw_job_on_position(j1, (0,0));
    draw_job_on_position(j2, (0,2));
    draw_job_on_position(j3, (1,2));
    draw_job_on_position(j4, (4,0));

    shipout("gantt_easy");
}

void figure_gantt_switch_off()
{
    // Let's define the jobs
    Job jobs[] = generate_workload();
    Job energy_jobs[] = generate_energy_jobs();
    Job j1, j2, j3, j4, json, jsoff, joff;

    j1 = jobs[0];
    j2 = jobs[1];
    j3 = jobs[2];
    j4 = jobs[3];
    json = energy_jobs[0];
    jsoff = energy_jobs[1];
    joff = energy_jobs[2];

    // Let's draw the frame
    draw_frame(0,7, 0,4);

    // Let's draw the jobs
    draw_job_on_position(j1, (0,0));
    draw_job_on_position(j2, (0,2));
    draw_job_on_position(j3, (1,2));
    draw_job_on_position(j4, (5,0));
    draw_job_on_position(jsoff, (2,0));
    draw_job_on_position(jsoff, (2,1));
    draw_job_on_position(json, (3,0));
    draw_job_on_position(json, (3,1));

    shipout("gantt_switch_off");
}

void figure_gantt_offline()
{
    // Let's define the jobs
    Job jobs[] = generate_workload();
    Job energy_jobs[] = generate_energy_jobs();
    Job j1, j2, j3, j4, json, jsoff, joff;

    j1 = jobs[0];
    j2 = jobs[1];
    j3 = jobs[2];
    j4 = jobs[3];
    json = energy_jobs[0];
    jsoff = energy_jobs[1];
    joff = energy_jobs[2];

    // Let's draw the frame
    draw_frame(0,8, 0,4);

    // Let's draw the jobs
    draw_job_on_position(jsoff, (0,0));
    draw_job_on_position(jsoff, (0,1));
    draw_job_on_position(jsoff, (0,2));
    draw_job_on_position(jsoff, (0,3));

    draw_job_on_position(joff, (1,0));
    draw_job_on_position(joff, (1,1));
    draw_job_on_position(joff, (1,2));
    draw_job_on_position(joff, (1,3));

    draw_job_on_position(json, (3,0));
    draw_job_on_position(json, (3,1));
    draw_job_on_position(json, (3,2));
    draw_job_on_position(json, (3,3));

    draw_job_on_position(j1, (5,0));
    draw_job_on_position(j2, (7,0));
    draw_job_on_position(j3, (5,2));
    draw_job_on_position(j4, (8,0));

    shipout("gantt_offline");
}

figure_workload_example();
erase();

figure_gantt_easy();
erase();

figure_gantt_switch_off();
erase();

figure_gantt_offline();
erase();
